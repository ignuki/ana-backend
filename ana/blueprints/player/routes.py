import os
from schema import Schema, And, Use, Optional

from flask import jsonify, request, url_for
from flask import current_app as app

from ana.blueprints.player.bp import bp

@bp.route('/player/test', methods=['GET'])
def player_test():
    return jsonify(success=True)

@bp.route('/queue/', defaults={'q_length': '25'}, methods=['GET'])
@bp.route('/queue/<path:q_length>', methods=['GET'])
def get_queue(q_length: str):
    queue_list = sorted(list(app.play_queue.queue))
    res = []
    for i in range(0, min(len(queue_list), int(q_length))):
        res.append(
            {
                'index': i,
                'path': str(queue_list[i].item),
                'filename': queue_list[i].item.name,
                'priority': queue_list[i].priority
            }
        )
    return jsonify(res)

@bp.route('/now_playing', methods=['GET'])
def now_playing():
    if app.now_playing == None:
        res = {}
    else:
        res= {
            'path': str(app.now_playing.item),
            'filename': app.now_playing.item.name
        }
    return jsonify(res)

def validate_posted_path(path: str):
    if not (os.path.isfile(abs_path) or os.path.isdir(abs_path)):
        return False

    if not path.startswith(
            os.path.abspath(app.config['PLAYER_MEDIA_DIR']) + os.sep):
        return False

    return True

new_queue_schema = Schema({
    'pool': [
        And(lambda s: validate_posted_path(s))
    ],
    Optional('shuffle'): And(Use(bool))
})

@bp.route('/new_queue', methods=['POST'])
def new_queue():
    json = request.get_json()
    try:
        new_queue_schema.validate(json)
    except Exception as e:
        app.logger.error('Exception validating schema: {}'.format(str(e)))
        return jsonify(success=False, exception=str(e)), 400

    if len(json['pool']) > 0:
        app.update_pool(json['pool'])

    if json.get('shuffle') is None:
        json['shuffle'] = True

    app.new_queue(json['shuffle'])
    app.start_queue()

    return jsonify(success=True)

@bp.route('/skip', methods=['POST'])
def skip():
    app.skip()
    return jsonify(success=True)

@bp.route('/prev', methods=['POST'])
def prev():
    if len(app.history) == 0:
        return jsonify(success=False)
    item = app.history.pop().item
    priority = app.queue_get_first_priority()
    if app.now_playing is not None:
        app.queue_put(priority, app.now_playing.item)
    app.queue_put(priority - 1, item)
    app.skip()
    return jsonify(success=True)
