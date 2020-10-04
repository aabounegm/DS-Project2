from pathlib import Path
from typing import List

from flask import abort
from werkzeug.datastructures import FileStorage

from src.config import storage_root
from src.extensions import mongo


def validate_path(path: str) -> Path:
    full_path = (storage_root/path).resolve()

    try:
        return full_path.relative_to(storage_root)
    except ValueError:
        abort(400, 'Invalid path specified.')


def get_min_free_space() -> int:
    return next(mongo.db.servers.aggregate([
        {'$group': {
            '_id': 0,
            'min_free_space': { '$min': '$free_space' }
        }}
    ]))['min_free_space']


def choose_server(among: List[str] = None):
    if among is None:
        return mongo.db.servers.find_one()['_id']

    return next(mongo.db.servers.aggregate([
        {'$match': {'_id': {'$in': among}}}
    ]))['_id']


def get_file_size(file: FileStorage) -> int:
    file.seek(0, 2)
    file_size = file.tell()
    file.seek(0)
    return file_size
