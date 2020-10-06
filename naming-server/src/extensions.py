"""Flask extensions are instantiated here.

To avoid circular imports with views and create_app(), extensions are instantiated here.
They will be initialized (calling init_app()) in app.py.
"""

from flask_pymongo import PyMongo
from flask_cors import CORS


mongo = PyMongo()
cors = CORS()
