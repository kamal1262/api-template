import logging

from flask import current_app
from flask_restplus import Resource


class HomeApi(Resource):
    def __init__(self, *args, **kwargs):
        self.message_producer = current_app.message_producer
        self.logger: logging.Logger = current_app.logger

    def get(self):
        self.message_producer.publish("api-template-queue", "test")
        self.logger.info("ok")
        return "Welcome"
