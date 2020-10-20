import os
import queue
import threading
import subprocess

import time # remove

from threading import current_thread
from pathlib import Path
from flask import Blueprint

from ana.app import Player
from flask import current_app as app

bp = Blueprint('player', __name__)

def play_queue():
    thread = current_thread()
    app.logger.info('Starting queue...')
    while True:
        app.now_playing = app.play_queue.get()
        app.logger.info('Now playing: {}'.format(
            app.now_playing.item.name
        ))
        # omxp_cmd = ["omxplayer", "-o", "hdmi", str(app.now_playing.item)]
        omxp_cmd = [
            "bash", "-c",
            "sleep 15 && echo '{} done'".format(str(app.now_playing.item))
        ]
        thread.omxp_process = subprocess.Popen(omxp_cmd, close_fds=True)
        app.history.append(app.now_playing)
        if len(app.history) > app.config['MAX_HISTORY_LEN']:
            app.history.pop(0)
        thread.omxp_process.wait()
        if thread.stopped():
            break
    app.logger.info('Exiting player thread')

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
        app.config['PLAYER_MEDIA_DIR'].rstrip('/') + '/' + \
        app.config['PLAYER_DEFAULT_SUF_DIR']

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
    app.start_queue(play_queue)
