import unittest
from queue import Queue

from flask.testing import FlaskClient

from webapp import create_app  # noqa: E402


@unittest.skip("API does not necessary to have MessageQueue")
class MessageQueueTests(unittest.TestCase):
    # executed prior to each test
    def setUp(self):
        self.app = create_app("config.TestConfig")

        self.client: FlaskClient = self.app.test_client()
        self.app_context = self.app.app_context()

    def tearDown(self):
        pass

    def test_send_message_to_queue(self):
        with self.app_context:
            topic = "topic"
            message = "message"
            self.app.message_producer.publish(topic, message)
            queue: Queue = self.app.message_producer.get_queue(topic)
            assert queue.get() == message

    def test_send_message_to_non_configured_queue(self):
        with self.app_context:
            invalid_topic = "invalid_topic"
            message = "message"
            with self.assertRaises(Exception) as context:
                self.app.message_producer.publish(invalid_topic, message)
            self.assertTrue(
                f"Topic {invalid_topic} is not found/configured properly"
                in str(context.exception)
            )
