from queue import Queue
from threading import Thread

from flask import Flask, current_app
import time


class InMemoryConsumer:
    def __init__(self, app: Flask, topic: str):
        if current_app.message_publisher:
            self.interval = current_app.config["TOPIC_INTERVAL"]
            self.logger = current_app.logger
            self.queue = current_app.message_publisher.get_queue(topic)
            if self.queue is None:
                self.queue = Queue(maxsize=0)
            worker = Thread(target=self.process, args=(self.queue,))
            worker.setDaemon(True)
            worker.start()

    def process(self, queue: Queue):
        while True:
            self.logger.info(queue.get())
            queue.task_done()
            time.sleep(self.interval)
