import queue
import threading
import os, signal
from random import shuffle as shuffle_list
import logging
from flask import Flask
from flask_cors import CORS
from pathlib import PosixPath
from subprocess import Popen, DEVNULL

from dataclasses import dataclass, field
from typing import Any

from flask import current_app as app

def play_queue():
    thread = threading.current_thread()
    app.logger.info('Starting queue...')
    while True:
        app.now_playing = app.play_queue.get()
        if not os.path.isfile(str(app.now_playing.item)):
            if thread.stopped():
                break
            else:
                continue
        app.logger.info('Now playing: {}'.format(
            str(app.now_playing.item)
        ))
        # omxp_cmd = ["omxplayer", "-o", "hdmi", str(app.now_playing.item)]
        omxp_cmd = ["sleep", "60"]
        thread.omxp_process = Popen(
            omxp_cmd, close_fds=True, stdout=DEVNULL,
            preexec_fn=os.setsid
        )
        thread.omxp_process.wait()
        app.history.append(app.now_playing)
        if app.now_playing.priority == float('inf'):
            if len(app.history) > app.config['MAX_HISTORY_LEN']:
                app.history.pop(0)
        if thread.stopped():
            break
    app.logger.info('Exiting player thread')

@dataclass(order=True)
class QueueItem:
    priority: float
    item: Any=field(compare=False)

    def __init__(self, priority, item):
        self.priority = priority
        self.item = item

# Pass the application context to our threads
class PlayerThread(threading.Thread):
    app: Flask
    _stop_event: threading.Event
    omxp_process: Popen

    def __init__(self, app: Flask, *args, **kwargs):
        self.app = app
        self._stop_event = threading.Event()
        super().__init__(*args, **kwargs)

    def run(self):
        with self.app.app_context():
            super().run()

    def kill_omxp(self):
        self.app.logger.warning('Killing PID {}'.format(self.omxp_process.pid))
        pgid = os.getpgid(self.omxp_process.pid)
        os.killpg(pgid, signal.SIGTERM)

    def stop(self):
        if not self.is_alive():
            return
        self._stop_event.set()
        self.kill_omxp()

    def stopped(self):
        return self._stop_event.is_set()

class Player(Flask):
    history: list
    queue_pool: list
    play_thread: PlayerThread
    now_playing: QueueItem
    play_queue: queue.PriorityQueue

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history = []
        self.queue_pool = []
        self.play_queue = None
        self.play_thread = None
        self.now_playing = None
        self.config.from_object('ana.default_settings.Config')

    def update_pool(self, pool: list):
        self.queue_pool = list(map(lambda e: QueueItem(float('inf'), e), pool))

    def new_queue(self, shuffle=True):
        shuf = self.queue_pool.copy()
        if shuffle is True:
            shuffle_list(shuf)
        self.play_queue = queue.PriorityQueue(maxsize=0)
        for item in shuf:
            self.play_queue.put(item)

    def skip(self):
        if self.play_thread is not None:
            if len(list(app.play_queue.queue)) == 0:
                self.play_thread.stop()
                self.play_thread.kill_omxp()
                self.play_thread.join()
                self.new_queue()
                self.start_queue()
            else:
                self.play_thread.kill_omxp()

    def start_queue(self, f=play_queue):
        if self.play_thread is not None:
            self.play_thread.stop()
            self.play_thread.join()
        self.play_thread = PlayerThread(self, target=f, args=(), daemon=True)
        self.play_thread.start()

    def queue_get_first_priority(self):
        l = sorted(list(self.play_queue.queue))
        if len(l) < 1:
            return float('inf')
        priority = l[0].priority
        return 99999 if priority == float('inf') else priority - 1

    def queue_put(self, priority: float, item: PosixPath):
        self.play_queue.put(QueueItem(priority, item))

from ana.blueprints.explorer import bp as bp_explorer
from ana.blueprints.player import bp as bp_player


def create_app():
    app = Player(__name__)
    cors = CORS(app)

    logging.basicConfig(level=logging.INFO)

    bp_explorer.config(app)
    bp_player.config(app)

    @app.route('/health')
    def health():
        return '', 200

    return app
