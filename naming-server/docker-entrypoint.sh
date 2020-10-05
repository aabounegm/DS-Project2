#!/bin/sh
# Start the Mongo daemon
mongod --fork --logpath /app/mongod.log

# Run our Flask application
# gunicorn --bind :7507 --log-level=info --access-logfile - run:app
python3.8 run.py
