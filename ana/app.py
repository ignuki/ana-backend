import queue
import random
import logging
from flask import Flask
from pathlib import PosixPath

from dataclasses import dataclass, field
from typing import Any

import threading

@dataclass(order=True)
class QueueItem:
    priority: float
    item: Any=field(compare=False)

    def __init__(self, priority, item):
        self.priority = priority
        self.item = item

# Pass the application context to our threads
class PlayerThread(threading.Thread):
    def __init__(self, app, *args, **kwargs):
        self.omxp_pid = None
        self.app = app
        self._stop_event = threading.Event()
        super().__init__(*args, **kwargs)

    def run(self):
        with self.app.app_context():
            super().run()

    def stop(self):
        if not self.is_alive():
            return
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

class Player(Flask):
    queue_pool = []
    play_thread: PlayerThread = None
    now_playing: QueueItem = None
    play_queue: queue.PriorityQueue = None
    history = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config.from_object('ana.default_settings.Config')

    def update_pool(self, pool: list):
        self.queue_pool = list(map(lambda e: QueueItem(float('inf'), e), pool))

    def new_queue(self, shuffle=True):
        shuf = self.queue_pool.copy()
        if shuffle is True:
            random.shuffle(shuf)
        self.play_queue = queue.PriorityQueue(maxsize=0)
        for item in shuf:
            self.play_queue.put(item)

    def skip(self):
        if self.play_thread is not None:
            self.logger.warning(
                'Killing PID {}'.format(self.play_thread.omxp_process.pid)
            )
            self.play_thread.omxp_process.kill()

    def start_queue(self, f):
        if self.play_thread is not None:
            self.play_thread.stop()
            self.logger.warning(
                'Killing PID {}'.format(self.play_thread.omxp_process.pid)
            )
            self.play_thread.omxp_process.kill()
            self.play_thread.join()
        self.play_thread = PlayerThread(
            self, target=f, args=(), daemon=True
        )
        self.play_thread.start()

    def get_now_playing(self):
        if self.now_playing == None:
            return {}
        return {
            'path': str(self.now_playing.item),
            'filename': self.now_playing.item.name
        }

    def queue_put(self, priority: float, item: PosixPath):
        self.play_queue.put(QueueItem(priority, item))

from ana.blueprints.explorer import bp as bp_explorer
from ana.blueprints.player import bp as bp_player


def create_app():
    app = Player(__name__)

    logging.basicConfig(level=logging.INFO)

    bp_explorer.config(app)
    bp_player.config(app)

    @app.route('/health')
    def health():
        return '', 200

    return app
