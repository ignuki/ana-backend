import os
from flask import Blueprint

from ana.app import Player

bp = Blueprint('explorer', __name__)

from ana.blueprints.explorer import routes


def config(app: Player):
    app.logger.info('Setting up file explorer...')
    if os.path.isdir(app.config['PLAYER_MEDIA_DIR']) == False:
        app.logger.error('{} does not exist or it is not a directory'.format(
            app.config['PLAYER_MEDIA_DIR']
        ))
        exit(1)

    app.register_blueprint(bp)
