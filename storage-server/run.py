"""The run script.
May be executed directly to start a development server
or fed to servers like gunicorn using `run:app`."""

import os
import shutil
import sys

from dotenv import load_dotenv
load_dotenv()
import requests

from src.app import create_app
from src.config import storage_root, NAMING_SERVER


app = create_app()
PORT = os.environ.get('PORT', 7508)

if __name__ == '__main__':
    file_listing = {
        '/' + str(child.relative_to(storage_root)): int(child.stat().st_mtime)
        for child in storage_root.rglob('*')
    }

    ok = True
    try:
        resp = requests.post(f'http://{NAMING_SERVER}/join',
                             json={'files': file_listing,
                                   'free_space': shutil.disk_usage(storage_root)[2],
                                   'port': PORT})
    except requests.exceptions.ConnectionError:
        ok = False

    ok = ok and resp.ok
    if not ok:
        print('Failed to join the DFS')
        sys.exit(1)
    else:
        missing_files = resp.json()
        for file in missing_files:
            resp = requests.get(f'http://{missing_files[file]}/file{file}')
            if resp.ok:
                (storage_root/file[1:]).parent.mkdir(parents=True, exist_ok=True)
                (storage_root/file[1:]).write_bytes(resp.content)
    app.run(host='0.0.0.0', port=PORT, debug=False)
