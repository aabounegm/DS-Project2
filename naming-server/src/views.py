"""Views related to file management.

StaticFile:
- POST /file
- GET /file/{file_id}
- DELETE /file/{file_id}
"""

import logging
import mimetypes
from pathlib import Path

import requests
from flask import jsonify, request, abort, current_app
from flask.views import MethodView

from src.config import storage_root
from src.blueprints import api
from src.extensions import mongo
from src.utils import (
    validate_path,
    get_min_free_space,
    choose_server,
    get_file_size,
)


NO_PAYLOAD = ('', 204)
log = logging.getLogger(__name__)
# pylint: disable=no-self-use


class FileAPI(MethodView):
    """The API for manipulating files on the naming server."""
    def get(self, path: str):
        """Retrieve a file under a given path."""
        internal_path = validate_path(path)

        parent = Path('/')
        entry = None
        for part in internal_path.parts:
            entry = mongo.db.index.find_one({'name': part, 'parent': str(parent)})
            if entry is None:
                abort(404)
            parent /= part

        if entry['is_directory'] or not entry['servers']:
            abort(404)

        server = choose_server(among=entry['servers'])

        file = requests.get(f'http://{server}/{internal_path}')
        if not file.ok:
            abort(400, 'File download failed.')

        response = current_app.make_response(file.content)
        response.headers.set('Content-Type', mimetypes.guess_type(internal_path.name)[0])
        return response

    def post(self, path: str):
        """Create a file under a given path."""
        if 'file' not in request.files:
            abort(400, 'No file attached.')
        file = request.files['file']

        internal_path = validate_path(path)

        *parents, name = internal_path.parts
        parent = Path('/')
        entry = None
        for part in parents:
            entry = mongo.db.index.find_one({'name': part, 'parent': str(parent)})
            if entry is None:
                mongo.db.index.insert_one({'name': part,
                                           'parent': str(parent),
                                           'is_directory': True})
            parent /= part

        entry = mongo.db.index.find_one({'name': name, 'parent': str(parent)})
        if entry is not None:
            abort(400, 'A file with this name already exists.')

        ok_servers = []
        for server in mongo.db.servers.find():
            response = requests.post(f'http://{server["_id"]}/{internal_path}',
                                     files={'file': file.stream})
            if not response.ok:
                continue

            server['free_space'] = int(response.text)
            mongo.db.servers.replace_one({'_id': server['_id']}, server)
            ok_servers.append(server['_id'])

        mongo.db.index.insert_one({
            'name': name,
            'parent': str(parent),
            'is_directory': False,
            'size': get_file_size(file),
            'servers': ok_servers,
        })

        return jsonify(get_min_free_space())

    def put(self, path):
        """Update a file under a given path."""
        if 'file' not in request.files:
            abort(400, 'No file attached.')
        file = request.files['file']

        internal_path = validate_path(path)

        *parents, name = internal_path.parts
        parent = Path('/')
        entry = None
        for part in parents:
            entry = mongo.db.index.find_one({'name': part, 'parent': str(parents)})
            if entry is None:
                mongo.db.index.insert_one({'name': part,
                                           'parent': str(parent),
                                           'is_directory': True})
            parent /= part

        entry = mongo.db.index.find_one({'name': name, 'parent': str(parent)})
        if entry is not None:
            abort(400, 'A file with this name already exists.')

        ok_servers = []
        for server in mongo.db.servers.find():
            response = requests.post(f'http://{server["_id"]}/{internal_path}',
                                     files={'file': file.stream})
            if not response.ok:
                continue

            server['free_space'] = int(response.text)
            mongo.db.servers.replace_one({'_id': server['_id']}, server)
            ok_servers.append(server['_id'])

        mongo.db.index.update_one(
            {
                'name': name,
            },
            {
                'name': name,
                'parent': str(parent),
                'is_directory': False,
                'size': get_file_size(file),
                'servers': ok_servers,
            },
            upsert=True
        )

        return jsonify(get_min_free_space())

    def delete(self, path):
        """Delete a file under a given path."""
        internal_path = validate_path(path)

        parent = Path('/')
        entry = None
        for part in internal_path.parts:
            entry = mongo.db.index.find_one({'name': part, 'parent': str(parent)})
            if entry is None:
                abort(404)
            parent /= part

        if entry['is_directory']:
            abort(404)

        for server in entry['servers']:
            response = requests.delete(f'http://{server}/{internal_path}')
            mongo.db.servers.update_one(
                {'_id': server},
                {'_id': server, 'free_space': int(response.text)},
            )

        return jsonify(get_min_free_space())

file_api = FileAPI.as_view('file_api')
api.add_url_rule('/file/<path>',
                 view_func=file_api,
                 methods=('GET', 'POST', 'PUT', 'DELETE'))
