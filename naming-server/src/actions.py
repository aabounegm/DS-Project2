import requests

from src.extensions import mongo


def heartbeat():
    servers = mongo.db.servers.find()
    for server in servers:
        response = requests.get('http://{server["_id"]/heartbeat}')
        if not response.ok:
            affected_files = mongo.db.index.find({
                'is_directory': False,
                'servers': server['_id'],
            })
            for file in affected_files:
                file['servers'].remove(server['_id'])
                mongo.db.update_one({'_id': file['_id']}, file)

            mongo.db.servers.delete_one(server)
