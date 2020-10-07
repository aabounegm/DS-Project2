from flask import jsonify, request, abort, current_app
from flask.views import MethodView
import os
import shutil

from src.blueprints import app
from src.config import storage_root


#==============================================heartbeat<3=========================

@app.route('/heartbeat' , methods=['GET'])
def heartbeat():
    return ('', 204)


class FileAPI(MethodView):
    #==============================================reading file=========================
    def get(self, pathToFile: str):
        full_path = storage_root/pathToFile

        if full_path.exists():
            response = current_app.make_response(full_path.read_bytes())
            return response
        else:
            abort(404)
#       return jsonify({"text : ":pathToFile})

    #==============================================create file=========================

    def post(self, pathToFile: str):
        #data = request.get_json()
        full_path = storage_root/pathToFile
        fileContent= request.files['file'].read()

        if full_path.exists():
            abort(404)
        else:
            full_path.parent.mkdir(parents= True, exist_ok = True)
            full_path.write_bytes(fileContent)
            return str(shutil.disk_usage(storage_root)[2])


    #==============================================Update file=========================

    def put(self, pathToFile):
        full_path = storage_root/pathToFile
        fileContent= request.files['file'].read()

        full_path.parent.mkdir(parents= True, exist_ok = True)
        full_path.write_bytes(fileContent)
        return str(shutil.disk_usage(storage_root)[2])

    #==============================================Delete file=========================
    def delete(self, pathToFile):
        full_path = storage_root/pathToFile
        full_path.unlink(missing_ok=True)
        return str(shutil.disk_usage(storage_root)[2])

file_api = FileAPI.as_view('file_api')
app.add_url_rule('/file/<path:path>',
                 view_func=file_api,
                 methods=('GET', 'POST', 'PUT', 'DELETE'))
app.add_url_rule('/file/',
                 view_func=file_api,
                 defaults={'path': ''},
                 methods=('GET', 'POST', 'PUT', 'DELETE'))

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
