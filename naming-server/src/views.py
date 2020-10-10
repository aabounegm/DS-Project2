import io
import logging
import mimetypes
import time
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

        if entry is None or entry['is_directory'] or not entry['servers']:
            abort(404)

        server = choose_server(among=entry['servers'])

        file = requests.get(f'http://{server}/file/{internal_path}')
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
            response = requests.post(f'http://{server["_id"]}/file/{internal_path}',
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
            'last_modified': int(time.time()),
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
            response = requests.post(f'http://{server["_id"]}/file/{internal_path}',
                                     files={'file': file.stream})
            if not response.ok:
                continue

            server['free_space'] = int(response.text)
            mongo.db.servers.replace_one({'_id': server['_id']}, server)
            ok_servers.append(server['_id'])

        mongo.db.index.replace_one(
            {
                'name': name,
            },
            {
                'name': name,
                'parent': str(parent),
                'is_directory': False,
                'size': get_file_size(file),
                'last_modified': int(time.time()),
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
            response = requests.delete(f'http://{server}/file/{internal_path}')
            mongo.db.servers.replace_one(
                {'_id': server},
                {'_id': server, 'free_space': int(response.text)},
            )

        mongo.db.index.delete_one(entry)

        return jsonify(get_min_free_space())

file_api = FileAPI.as_view('file_api')
api.add_url_rule('/file/<path:path>',
                 view_func=file_api,
                 methods=('GET', 'POST', 'PUT', 'DELETE'))
api.add_url_rule('/file/',
                 view_func=file_api,
                 defaults={'path': ''},
                 methods=('GET', 'POST', 'PUT', 'DELETE'))


class DirectoryAPI(MethodView):
    """The API for manipulating directories on the naming server."""
    def get(self, path: str):
        """Retrieve the listing of a given directory."""
        internal_path = validate_path(path)

        parent = Path('/')
        entry = {'name': '.', 'is_directory': True}
        for part in internal_path.parts:
            entry = mongo.db.index.find_one({'name': part, 'parent': str(parent)})
            if entry is None:
                abort(404)
            parent /= part

        if not entry['is_directory']:
            abort(404)

        children = mongo.db.index.find({'parent': str(parent)})
        listing = []
        for child in children:
            if child['is_directory']:
                listing.append({
                    'name': child['name'],
                    'path': str(Path('/') / internal_path / child['name']) + '/',
                    'is_directory': True,
                })
            else:
                listing.append({
                    'name': child['name'],
                    'path': str(Path('/') / internal_path / child['name']),
                    'is_directory': False,
                    'size': child['size'],
                    'replicas': len(child['servers']),
                })

        return jsonify(listing)

    def post(self, path: str):
        """Create a directory."""
        internal_path = validate_path(path)

        parent = Path('/')
        entry = None
        for part in internal_path.parts:
            entry = mongo.db.index.find_one({'name': part, 'parent': str(parent)})
            if entry is None:
                entry = {'name': part,
                         'parent': str(parent),
                         'is_directory': True}
                mongo.db.index.insert_one(entry)
            parent /= part

        if not entry['is_directory']:
            abort(400, 'A file with this name already exists.')

        return NO_PAYLOAD

    def delete(self, path: str):
        """Delete a directory."""
        internal_path = validate_path(path)

        parent = Path('/')
        entry = None
        for part in internal_path.parts:
            entry = mongo.db.index.find_one({'name': part, 'parent': str(parent)})
            if entry is None:
                return NO_PAYLOAD
            parent /= part

        if not entry['is_directory']:
            abort(400, 'The path points to a file.')

        alright = str(parent).replace("/", "\\/")
        children = mongo.db.index.find({
            'parent': {'$regex': f'^{alright}.*'}
        })
        for child in children:
            if not child['is_directory']:
                for server in child['servers']:
                    response = requests.delete(
                        f'http://{server}/file{child["parent"]}/{child["name"]}'
                    )
                    mongo.db.servers.replace_one(
                        {'_id': server},
                        {'_id': server, 'free_space': int(response.text)},
                    )

            mongo.db.index.delete_one(child)

        mongo.db.index.delete_one(entry)

        return NO_PAYLOAD

directory_api = DirectoryAPI.as_view('directory_api')
api.add_url_rule('/dir/<path:path>',
                 view_func=directory_api,
                 methods=('GET', 'POST', 'DELETE'))
api.add_url_rule('/dir/',
                 view_func=directory_api,
                 defaults={'path': ''},
                 methods=('GET', 'POST', 'DELETE'))


@api.route('/initialize', methods=['POST'])
def initialize():
    """Wipe everything from the storage servers."""
    for server in mongo.db.servers.find():
        response = requests.post(f'http://{server["_id"]}/initialize')
        server['free_space'] = int(response.text)
        mongo.db.servers.replace_one({'_id': server['_id']}, server)

    mongo.db.index.remove()
    return jsonify(get_min_free_space())


@api.route('/join', methods=['POST'])
def join():
    """Add a storage server to the pool of servers."""
    mongo.db.servers.insert_one({
        '_id': f'{request.remote_addr}:{request.json["port"]}',
        'free_space': request.json['free_space']
    })

    file_index = mongo.db.index.find({})

    this_missing = {}
    for file in file_index:
        if file['is_directory']:
            continue

        full_name = f"{file['parent'].rstrip('/')}/{file['name']}"
        if file['last_modified'] != request.json['files'].get(full_name, None):
            this_missing[full_name] = choose_server(among=file['servers'])
            file['servers'].append(f'{request.remote_addr}:{request.json["port"]}')
            mongo.db.index.replace_one({'_id': file['_id']}, file)

    return jsonify(this_missing)


@api.route('/free_space')
def free_space():
    """Return the amount of free space among the storage servers."""
    return jsonify(get_min_free_space())


@api.route('/copy/<path:path>', methods=['POST'])
def copy(path: str):
    """Copy the file to the specified location."""
    src_internal_path = validate_path(path)
    dst_internal_path = validate_path(request.json["destination"].lstrip('/'))

    src_parent = Path('/')
    src_entry = None
    for part in src_internal_path.parts:
        src_entry = mongo.db.index.find_one({'name': part, 'parent': str(src_parent)})
        if src_entry is None:
            abort(404)
        src_parent /= part

    if src_entry is None or src_entry['is_directory'] or not src_entry['servers']:
        abort(404)

    *dst_parents, dst_name = dst_internal_path.parts
    dst_parent = Path('/')
    dst_entry = None
    for part in dst_parents:
        dst_entry = mongo.db.index.find_one({'name': part, 'parent': str(dst_parent)})
        if dst_entry is None:
            mongo.db.index.insert_one({'name': part,
                                       'parent': str(dst_parent),
                                       'is_directory': True})
        dst_parent /= part

    dst_entry = mongo.db.index.find_one({'name': dst_name, 'parent': str(dst_parent)})
    if dst_entry is not None:
        abort(400, 'A file with this name already exists.')

    server = choose_server(among=src_entry['servers'])

    file = requests.get(f'http://{server}/file/{src_internal_path}')
    if not file.ok:
        abort(400, 'Copying failed.')

    ok_servers = []
    for server in mongo.db.servers.find():
        response = requests.post(
            f'http://{server["_id"]}/file/{str(dst_internal_path)}',
            files={'file': io.BytesIO(file.content)}
        )
        if not response.ok:
            continue

        server['free_space'] = int(response.text)
        mongo.db.servers.replace_one({'_id': server['_id']}, server)
        ok_servers.append(server['_id'])

    mongo.db.index.insert_one({
        'name': dst_name,
        'parent': str(dst_parent),
        'is_directory': False,
        'size': len(file.content),
        'last_modified': int(time.time()),
        'servers': ok_servers,
    })

    return jsonify(get_min_free_space())
