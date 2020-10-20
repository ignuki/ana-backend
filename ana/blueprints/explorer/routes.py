import os

from ana.blueprints.explorer.bp import bp

from flask import jsonify, request, url_for
from flask import current_app as app


@bp.route('/explorer/test', methods=['GET'])
def explorer_test():
    return jsonify(success=True)

@bp.route('/ls/', defaults={'ls_path': ''}, methods=['GET'])
@bp.route('/ls/<path:ls_path>', methods=['GET'])
def ls_dir(ls_path: str):
    abs_path = app.config['PLAYER_MEDIA_DIR'].rstrip(os.sep) + os.sep + ls_path
    if os.path.isfile(abs_path) == True:
        return jsonify(
            location = abs_path,
            filename = abs_path.split(os.sep)[-1]
        )
    if os.path.isdir(abs_path) == False:
        return jsonify(
            message = '{} does not exist.'.format(abs_path)
        ), 404
    res = next(os.walk(abs_path))
    return jsonify(
        location = abs_path,
        dirname =abs_path.split(os.sep)[-1],
        ls = {
            'dirs':  res[1],
            'files': res[2]
        }
    )
