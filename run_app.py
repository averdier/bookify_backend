# -*- coding: utf-8 -*-

import os
import logging
from app import create_app

logging.basicConfig(level=logging.INFO)

app = create_app(os.environ.get('APP_CONFIG', 'default'))


if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555

    app.run(HOST, PORT, debug=True) # On Windows
    #app.run(HOST, PORT, debug=True, processes=3) # On Linux
    #app.run('0.0.0.0', PORT, debug=True) # On docker