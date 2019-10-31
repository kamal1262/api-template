from queue import Queue

from flask import Flask


class InMemoryPublisher:
    def __init__(self, app: Flask):
        self.q = {}
        for item in app.config.get("MESSAGE_TOPICS"):
            self.q[item] = Queue(maxsize=0)
        self.q["__default__"] = Queue(maxsize=0)

    def publish(self, topic: str, message: str):
        if topic in self.q:
            self.q.get(topic).put(message)
        else:
            raise Exception(f"Topic {topic} is not found/configured properly")

    def get_queue(self, topic: str) -> Queue:
        return self.q.get(topic)
