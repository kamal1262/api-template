import time
from threading import Thread

import boto3
from flask import Flask, current_app


class SQSConsumer:
    def __init__(self, app: Flask, topic: str):
        self.logger = current_app.logger
        self.sqs_client = boto3.client("sqs", region_name="ap-southeast-1")
        self.queue = None

        if current_app.message_publisher:
            self.queue = current_app.message_publisher.get_queue(topic)
        else:
            client_response = self.sqs_client.get_queue_url(QueueName=topic)
            if "QueueUrl" in client_response:
                self.queue = client_response["QueueUrl"]

        if self.queue is None:
            raise Exception(f"Topic {topic} is not found/configured properly")

        worker = Thread(target=self.process, args=(self.sqs_client, self.queue))
        worker.setDaemon(True)
        worker.start()

    def process(self, sqs_client, queue):
        while True:
            messages = sqs_client.receive_message(QueueUrl=queue)
            if "Messages" in messages:
                for message in messages["Messages"]:
                    self.logger.info(message["Body"])
                    self.sqs_client.delete_message(
                        QueueUrl=queue, ReceiptHandle=message["ReceiptHandle"]
                    )
            time.sleep(30)
