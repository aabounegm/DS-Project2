# DS Project 2

This is a distributed file system with a focus on fault tolerance.

The system contains the following components:

* Storage servers
* Naming server
* Client


## Storage server

The main goal of the storage server is to store, index and serve file data.
The files will be indexed using the path inside the file system – that is, the location and filename are stored on the storage server.

It will use the following REST API:

* `GET /heartbeat`  
  The _heartbeat_ request. If the storage server is healthy, it should return 204.

* `GET /file/<path>`  
  Fetch the content of the file with the specified path.

  If the file exists, the server will send back the content of that file.  
  If the path points to a directory or the path is invalid, the server should return 404.  
  If the path points to an illegal location (outside the root), the server should return 400.  

* `POST /file/<path>`  
  Create a file with the specified contents on the specified path.  
  The request body should contain the content of the file to upload with the name `file` (e.g. `requests.post(addr, files={"file": ...})`).

  On success, the server should respond with 200 and the amount of free storage on the storage server in bytes.  
  If the specified path to the file contains inexistent directories, they should be automatically created.  
  If the path points to an existing file, the server should return 400.  
  If the path points to an illegal location (outside the root), the server should return 400.  

* `PUT /file/<path>`  
  Update (or create, if it doesn't exist) a file with the specified contents on the specified path.  
  The request body should contain the content of the file to upload with the name `file` (e.g. `requests.post(addr, files={"file": ...})`).

  On success, the server should respond with 200 and the amount of free storage on the storage server in bytes.  
  If the specified path to the file contains inexistent directories, they should be automatically created.  
  If the path points to an illegal location (outside the root), the server should return 400.  

* `DELETE /file/<path>`  
  Delete the file on the specified path.  
  If the deleted file is the last one in the directory, the directory should also be deleted.

  On success, the server should respond with 200 and the amount of free storage on the storage server in bytes.  
  If the path points to a directory or the path is invalid, the server should return 404.  
  If the path points to an illegal location (outside the root), the server should return 400.  

* `POST /synchronize`  
  Instruct the storage server to download/update certain files from other storage servers.

  Sample request:
  ```json
  {
    "/path1/path2/file1": "127.0.0.1",
    "/file2": "127.0.0.2"
  }
  ```

  On success, the server should respond with 200 and the amount of free storage on the storage server in bytes.  

* `POST /initialize`
  Delete everything inside the storage folder and return the available size in bytes.


## Naming server

The naming server contains three architectural parts:

* the REST API for clients
* storage server discovery
* storage server file synchronization

### The REST API

The REST API of the naming server will be similar to the REST API of the storage server with some additions.

* `GET /file/<path>`  
  The behaviour should be identical to that of the storage server, but additionally the server should set the correct `Content-Type` header on the response based on the filename.

* `POST /file/<path>`  
  The behaviour should be identical to that of the storage server.

* `PUT /file/<path>`  
  The behaviour should be identical to that of the storage server.

* `DELETE /file/<path>`  
  The behaviour should be identical to that of the storage server.

* `GET /dir/<path_to_directory>`  
  Fetch the listing of files in a directory.  
  The output will contain the information about files in the directory such as their name, size in bytes and the amount of replicas that exist of that file.

  Sample response:
  ```json
  [
    {
      "name": "file.txt",
      "is_directory": false,
      "size": 1337,
      "last_modified": 1338,
      "replicas": 2
    },
    {
      "name": "directory",
      "is_directory": true,
    }
  ]
  ```

  On success, the server should return 200 and the listing as a JSON array.  
  If the path points to a file or the path is invalid, the server should return 404.  
  If the path points to an illegal location (outside the root), the server should return 400.  

* `POST /dir/<path_to_directory>`  
  Create a directory on the naming server.  

  On success, the server should respond with 204.  
  If the specified path to the file contains inexistent directories, they should be automatically created.  
  If the path points to an existing directory, the server should return 204 as if the operation was successful.  
  If the path points to a file, the server should return 400.  
  If the path points to an illegal location (outside the root), the server should return 400.  

* `DELETE /dir/<path_to_directory>`  
  Delete a directory on the naming server.  

  On success, the server should respond with 204.  
  If the directory is not empty, the server should respond with 400 – only empty directories can be removed with this request.  
  If the directory doesn't exist, the server should respond with 204 as if the operation was successful.

* `POST /initialize`
  Wipe everything off the storage servers and create a clean slate.

  On success, the server should respond with 200 and the amount of free space in bytes.

* `POST /join`
  Join the set of storage servers.  
  This endpoint is used by storage servers upon initialization to register themselves with the naming server. The request body contains the current filesystem state of the storage server. This state contains the available storage space on the storage server in bytes and the mapping of filenames to their _last modified_ timestamp:

  Sample request body:  
  ```json
  {
    "port": 8080,
    "free_space": 1024,
    "files": {
      "/path1/path2/file1": 1337,
      "/file1": 1338,
      "/path1/file2": 1336
    }
  }
  ```

  The server will respond with a structure similar to that of the `/synchronize` endpoint instructing the newly joined server on where to download the missing files.

  Upon registering the storage server, the naming server adds an entry to a MongoDB collection `servers` with the address of the server and the amount of free space on the storage server in bytes. Sample document:
  ```json
  {
    "_id": "127.0.0.1",
    "free_space": 1024
  }
  ```


### Storage server discovery

The storage servers take the active role in the process of discovery, sending a `POST /join` request to the naming server.  
After the storage server has been registered with the naming server, the naming server should send heartbeat requests to the storage server to ensure it is still alive. If it happens that the server is down, its IP address should be removed from every file entry in the index on the naming server.


### Storage server file synchronization

Every storage server has a `POST /synchronize` endpoint. This endpoint will be used by the naming server to instruct a storage server that is missing some file to get it from another storage server. During the storage server discovery the naming server will receive the listing of files on every storage server. The naming server will merge the listing of that server with its own, compute the differences and send the instructions to the storage servers to get into a consistent state.

The naming server will maintain a data structure to keep track of stored files, called _the index_. This index will be powered by MongoDB.

The sample of this structure:
```json
[
  {
    "name": "path1",
    "location": "/",
    "is_directory": true,
  },
  {
    "name": "file1",
    "location": "/",
    "is_directory": false,
    "size": 1024,
    "last_modified": 1338,
    "servers": [
      "127.0.0.1",
      "127.0.0.2"
    ]
  },
  {
    "name": "path2",
    "location": "/path1",
    "is_directory": true,
  },
  {
    "name": "path3",
    "location": "/path1/path2",
    "is_directory": true,
  }
]
```


## Client

The client is a web application that is launched with an IP address of the naming server. This web application presents an interface to perform the following actions:

* Upload a file (allowing replacement)
* Download a file
* Delete a file
* Get file information (name, size, amount of servers that host a replica)
* Copy a file
* Move a file
* Create a directory
* Delete a directory (recursively deleting all its content)
* Traverse the file system

The client will keep the current working directory as internal state.

The client displays the information about the free space available on the filesystem. It is provided by the naming server which computes it as the minimum of free space on all of the storage servers.
