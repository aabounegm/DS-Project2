import requests

from src.extensions import mongo


def heartbeat():
    servers = mongo.db.servers.find()
    for server in servers:
        ok = True
        try:
            response = requests.get(f'http://{server["_id"]}/heartbeat')
        except requests.exceptions.ConnectionError:
            ok = False

        ok = ok and response.ok
        if not ok:
            affected_files = mongo.db.index.find({
                'is_directory': False,
                'servers': server['_id'],
            })
            for file in affected_files:
                file['servers'].remove(server['_id'])
                mongo.db.index.replace_one({'_id': file['_id']}, file)

            mongo.db.servers.delete_one(server)
