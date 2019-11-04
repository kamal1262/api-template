from flask import current_app


class SampleConsumer:
    def __init__(self, message_consumer):
        self.logger = current_app.logger
        message_consumer("api-template-queue", self.process_message)

    def process_message(self, message: str):
        self.logger.info(message)
        return True
