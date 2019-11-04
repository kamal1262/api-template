import abc
import time
from queue import Queue, Empty
from threading import Thread
from typing import Callable

import boto3
from flask import current_app


class MessageConsumer:
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def process(self, queue, func: Callable[[str], bool]):
        return


class InMemoryConsumer(MessageConsumer):
    def __init__(self, topic: str, func):
        if current_app.message_producer:
            self.interval = current_app.config["TOPIC_INTERVAL"]
            self.logger = current_app.logger
            self.queue = current_app.message_producer.get_queue(topic)
            if self.queue is None:
                self.queue = Queue(maxsize=0)
            worker = Thread(target=self.process, args=(self.queue, func))
            worker.setDaemon(True)
            worker.start()

    def process(self, queue, func):
        while True:
            try:
                task = queue.get(False)
            except Empty:
                pass
            else:
                if func(task):
                    queue.task_done()
            time.sleep(self.interval)


class SQSConsumer(MessageConsumer):
    def __init__(self, topic: str, func):
        self.interval = current_app.config["TOPIC_INTERVAL"]
        self.logger = current_app.logger
        self.sqs_client = boto3.client("sqs", region_name="ap-southeast-1")
        self.queue = None

        if current_app.message_producer:
            self.queue = current_app.message_producer.get_queue(topic)
        else:
            client_response = self.sqs_client.get_queue_url(QueueName=topic)
            if "QueueUrl" in client_response:
                self.queue = client_response["QueueUrl"]

        if self.queue is None:
            raise Exception(f"Topic {topic} is not found/configured properly")

        worker = Thread(target=self.process, args=(self.queue, func))
        worker.setDaemon(True)
        worker.start()

    def process(self, queue, func):
        sqs_client = boto3.client("sqs", region_name="ap-southeast-1")
        while True:
            messages = sqs_client.receive_message(QueueUrl=queue, MaxNumberOfMessages=3)
            if "Messages" in messages:
                for message in messages["Messages"]:
                    if func(message["Body"]):
                        sqs_client.delete_message(
                            QueueUrl=queue, ReceiptHandle=message["ReceiptHandle"]
                        )
            time.sleep(self.interval)
