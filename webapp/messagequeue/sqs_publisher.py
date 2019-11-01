import logging

import boto3
from botocore.exceptions import ClientError
from flask import Flask, current_app


class SQSPublisher:
    def __init__(self, app: Flask):
        self.logger: logging.Logger = current_app.logger
        self.sqs_client = boto3.client("sqs", region_name="ap-southeast-1")
        self.q = {}
        for item in app.config.get("MESSAGE_TOPICS"):
            self.q[item] = self.sqs_client.get_queue_url(QueueName=item)["QueueUrl"]

    def publish(self, topic: str, message: str):
        try:
            if topic in self.q:
                self.sqs_client.send_message(
                    QueueUrl=self.q.get(topic), MessageBody=message
                )
            else:
                raise Exception(f"Topic {topic} is not found/configured properly")

        except ClientError as e:
            self.logger.error(e)

    def get_queue(self, topic: str):
        return self.q.get(topic)
