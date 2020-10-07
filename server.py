from flask import Flask,jsonify, request, abort
from flask.views import MethodView
import os
import shutil
import pathlib


app = Flask(__name__)
storage_root = pathlib.Path(os.getenv('STORAGE_DIR', '/var/storage'))


file_api = FileAPI.as_view('file_api')
app.add_url_rule('/file/<path:path>',
                 view_func=file_api,
                 methods=('GET', 'POST', 'PUT', 'DELETE'))
app.add_url_rule('/file/',
                 view_func=file_api,
                 defaults={'path': ''},
                 methods=('GET', 'POST', 'PUT', 'DELETE'))

#==============================================heartbeat<3=========================

@app.route('/heartbeat' , methods=['GET'])
def heartbeat():
    return ('', 204)


class FileAPI(MethodView):
    #==============================================reading file=========================
    def get(self, pathToFile: str):
        full_path = storage_root/pathToFile 

        if full_path.exists():
                response = app.make_response(full_path.read_bytes())
                return response
        else:
            abort(404)
#       return jsonify({"text : ":pathToFile})
        
    #==============================================create file=========================

    def post0(self, pathToFile: str, fileContent):   

        folder=pathToFile[0:pathToFile.rfind('/')]
        f = open(pathToFile, "w")
        f.write(fileContent)
        f.close()
        memory = shutil.disk_usage(folder)  
        return str(memory[2])

    
    def post1(self, pathToFile: str):                          
        #data = request.get_json()
        full_path = storage_root/pathToFile
        fileContent= request.files['file'].read()
        
        folder=pathToFile[0:pathToFile.rfind('/')]    #to keep the path without the name of the file
        if os.path.exists(full_path):
            abort(404)
        else:  
            full_path.parent.mkdir(parents= True, exist_ok = True)
            
            
    #==============================================Update file=========================

    def put0(self, pathToFile, fileContent):
        #this is an auxiliary function to update a simple file with keeping the old content
        folder=pathToFile[0:pathToFile.rfind('/')]
        f = open(pathToFile, "a+")
        f.write(fileContent)
        f.close()
        memory = shutil.disk_usage(folder)  
        return str(memory[2])


    def put1(self, pathToFile):                    #this is the main function to update 
        full_path = storage_root/pathToFile
        fileContent= request.files['file'].read()
        
        folder=pathToFile[0:pathToFile.rfind('/')]    #to keep the path without the name of the file
        if os.path.exists(full_path):
            abort(404)
        else:  
            full_path.parent.mkdir(parents= True, exist_ok = True)

    #==============================================Delete file=========================
    def delete(self, pathToFile):
        folder=path[0:path.rfind('/')]
        if os.path.exists(path):
            os.remove(path)
            memory = shutil.disk_usage(folder) 
            if len(os.listdir(folder))==0:
                shutil.rmtree(folder)    #to delete a folder if it's empty
                #print("folder deleted")
            return str(memory[2]) 
        else:
            abort(404)
        
#==============================================Initialize folder=========================
    
@app.route('/INITIALIZE/<string:pth>', methods=['GET'])    
def initialize_folder(pth) :
    folder=path[0:path.rfind('\\')]
    for sub in os.listdir(pth) :
        if os.path.isdir(folder+"\\"+sub) :
            shutil.rmtree(folder+"\\"+sub)
        else:
            os.remove(folder+"\\"+sub)
    memory = shutil.disk_usage(folder)  
    return "the amount of free storage on the storage server in bytes is: "+str(memory[2]) 
            
if __name__ == '__main__':
    app.run()


