import os
import queue
import threading

import time # remove

from pathlib import Path
from flask import Blueprint

from ana.app import Player
from flask import current_app as app

bp = Blueprint('player', __name__)

from ana.blueprints.player import routes

def config(app: Player):
    app.logger.info('Setting up player...')

    if app.config.get('MAX_HISTORY_LEN') is None:
        app.config['MAX_HISTORY_LEN'] = 30
    elif app.config.get('MAX_HISTORY_LEN'):
        app.logger.error(
            '{} is not a valid value for MAX_HISTORY_LEN'.format(
                app.config['MAX_HISTORY_LEN']
            ))
        exit(1)

    pool_path = \
        app.config['PLAYER_MEDIA_DIR'].rstrip('/') + os.sep + \
        app.config['PLAYER_DEFAULT_SHUF_DIR']

    if os.path.isdir(pool_path) == False:
        app.logger.error('{} does not exist or it is not a directory'.format(
            pool_path
        ))
        exit(1)

    res = []
    res.extend(list(Path(pool_path).rglob("*.[aA][vV][iI]")))
    res.extend(list(Path(pool_path).rglob("*.[fF][lL][vV]")))
    res.extend(list(Path(pool_path).rglob("*.[mM][kK][vV]")))
    res.extend(list(Path(pool_path).rglob("*.[mM][oO][vV]")))
    res.extend(list(Path(pool_path).rglob("*.[mM][pP][4]")))
    res.extend(list(Path(pool_path).rglob("*.[mM][pP][eE][gG]")))
    res.extend(list(Path(pool_path).rglob("*.[mM][pP][gG]")))
    res.extend(list(Path(pool_path).rglob("*.[oO][gG][gG]")))
    res.extend(list(Path(pool_path).rglob("*.[wW][mM][vV]")))

    app.register_blueprint(bp)

    app.update_pool(res)
    app.new_queue()
    app.start_queue()
