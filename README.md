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

* `GET /status`  
  The _heartbeat_ request. If the storage server is healthy, it should respond to this request with the mapping of the files that it contains to their Last Modified timestamp.

  Sample output:
  ```json
  {
    "/path1/path2/file1": 1337,
    "/file1": 1338,
    "/path1/file2": 1336,
  }
  ```

* `GET /file/<path>`  
  Fetch the content of the file with the specified path.

* `POST /file/<path>`  
  Create a file with the specified contents on the specified path.
  The request body should contain the content of the file to upload.

  If the specified path to the file contains inexistent directories, they should be automatically created.

* `PUT /file/<path>`  
  Update (or create, if it doesn't exist) a file with the specified contents on the specified path.
  The request body should contain the content of the file to upload.

* `DELETE /file/<path>`  
  Delete the file on the specified path.

* `POST /synchronize`
  Instruct the storage server to download/update certain files from other storage servers.

  Sample request:
  ```json
  {
    "/path1/path2/file1": "127.0.0.1",
    "/file2": "127.0.0.2"
  }
  ```


## Naming server

The naming server contains three architectural parts:

* the REST API for clients
* storage server discovery
* storage server file synchronization

### The REST API

The REST API of the naming server will be identical to the REST API of the storage server with the following exceptions:

* `GET /status` will not be used

* `GET /dir/<path_to_directory>`  
  Fetch the listing of files in a directory.  
  The output may contain files and directories, the directories will have a trailing slash.

  Sample output:
  ```json
  [
    "file.txt",
    "directory/",
    "another_file.txt",
    "directory.txt/"
  ]
  ```

* `POST /dir/<path_to_directory>`  
  Create a directory on the naming server.  
  This directory will not appear on the storage servers until some file is created in it.

* `DELETE /dir/<path_to_directory>`  
  Delete a directory on the naming server.  
  The operation should fail if the directory is not empty – only empty directories can be removed with this request.


### Storage server discovery

The naming server will be created with the information about the subnet that it is placed in. It will go over the IP addresses in that subnet every minute, sending heartbeat requests to determine if the given server is up or down.


### Storage server file synchronization

Every storage server has a `POST /synchronize` endpoint. This endpoint will be used by the naming server to instruct a storage server that is missing some file to get it from another storage server. During the storage server discovery the naming server will receive the listing of files on every storage server. The naming server will merge the listing of that server with its own, compute the differences and send the instructions to the storage servers to get into a consistent state.

To do that, the naming server will keep a data structure that lists all files and the addresses of the servers that contain this file. The database backing this structure will be MongoDB.

The structure will keep a tree-like view of the file system with entries for files and directories, differentiated by the `is_directory` boolean field. The file entries also contain the size of the file in bytes.

The sample of this structure:
```json
[
  {
    "name": "path1",
    "is_directory": true,
    "contents": [
      {
        "name": "file1",
        "size": 1024,
        "is_directory": false,
        "servers": [
          "127.0.0.1",
          "127.0.0.2"
        ]
      }
    ]
  },
  {
    "name": "path2",
    "is_directory": true,
    "contents": []
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
