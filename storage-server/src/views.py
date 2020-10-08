from flask import jsonify, request, abort, current_app
from flask.views import MethodView
import requests
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
    def get(self, path: str):
        full_path = storage_root/path

        if full_path.exists():
            response = current_app.make_response(full_path.read_bytes())
            return response
        else:
            abort(404)
#       return jsonify({"text : ":pathToFile})

    #==============================================create file=========================

    def post(self, path: str):
        #data = request.get_json()
        full_path = storage_root/path
        fileContent= request.files['file'].read()

        if full_path.exists():
            abort(404)
        else:
            full_path.parent.mkdir(parents= True, exist_ok = True)
            full_path.write_bytes(fileContent)
            return str(shutil.disk_usage(storage_root)[2])


    #==============================================Update file=========================

    def put(self, path):
        full_path = storage_root/path
        fileContent= request.files['file'].read()

        full_path.parent.mkdir(parents= True, exist_ok = True)
        full_path.write_bytes(fileContent)
        return str(shutil.disk_usage(storage_root)[2])

    #==============================================Delete file=========================
    def delete(self, path):
        full_path = storage_root/path
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

@app.route('/initialize', methods=['POST'])
def initialize_folder() :
    shutil.rmtree(storage_root)
    storage_root.mkdir()
    memory = shutil.disk_usage(storage_root)
    return str(memory[2])


@app.route('/synchronize', methods=['POST'])
def synchronize():
    for file in request.json:
        resp = requests.get(f'http://{request.json[file]}{file}')
        if resp.ok:
            (storage_root/file[1:]).write_bytes(resp.content)
    memory = shutil.disk_usage(folder)
    return str(memory[2])
