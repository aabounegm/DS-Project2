"""Configuration variables."""

import os
import pathlib


storage_root = pathlib.Path(os.getenv('STORAGE_DIR', '/var/storage'))
MONGO_URI = os.getenv('MONGO_URI')
