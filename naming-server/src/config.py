"""Configuration variables."""

import os
import pathlib


storage_root = pathlib.Path(os.getenv('STORAGE_DIR', '/var/storage'))
