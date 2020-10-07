"""The run script.
May be executed directly to start a development server
or fed to servers like gunicorn using `run:app`."""

import os

from dotenv import load_dotenv
load_dotenv()

from src.app import create_app


app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 7507), debug=True)
