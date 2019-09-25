import unittest

from flask.testing import FlaskClient

from webapp import create_app  # noqa: E402


class HomeModuleTests(unittest.TestCase):
    # executed prior to each test
    def setUp(self):
        self.app = create_app("config.TestConfig")

        self.client: FlaskClient = self.app.test_client()
        self.app_context = self.app.app_context()

    def tearDown(self):
        pass

    def test_get_user(self):
        with self.client as c:
            request = c.get("/healthcheck")
            assert request.status_code == 200
