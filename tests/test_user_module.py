import json
import unittest

from flask.testing import FlaskClient
from flask_migrate import upgrade

from webapp import create_app, db  # noqa: E402
from webapp.user.models import User  # noqa: E402


class UserModuleTests(unittest.TestCase):
    # executed prior to each test
    def setUp(self):
        def __init_db():
            with self.app_context:
                upgrade(sql=True, directory="migrations")
                db.create_all()

        def __populate_test_data(users: []):
            for user in users:
                db.session.add(user)
            db.session.commit()

        self.test_user_1: User = User(
            id=999, username="test", email="test@test.com", password="123456"
        )
        self.app = create_app("config.TestConfig")

        self.client: FlaskClient = self.app.test_client()
        self.app_context = self.app.app_context()

        __init_db()
        __populate_test_data([self.test_user_1])

    def tearDown(self):
        db.session.remove()

    def test_get_user(self):
        with self.client as c:
            request = c.get("/api/users/999")
            data = json.loads(request.get_data(as_text=True))

            assert request.status_code == 200
            assert data["username"] == self.test_user_1.username
            assert data["email"] == self.test_user_1.email
            assert data["id"] == self.test_user_1.id

    # def test_get_non_existent_user(self):
    #     with self.client as c:
    #         request = c.get("/api/users/5000")
    #         assert request.status_code == 404

    def test_list_users(self):
        with self.client as c:
            request = c.get("/api/users")
            assert request.status_code == 200

    def test_update_user(self):
        with self.client as c:
            request = c.put(
                "/api/users/999",
                data=json.dumps(
                    {
                        "username": "new_username",
                        "password": "password",
                        "email": "test@test.com",
                    }
                ),
                content_type="application/json",
            )
            data = json.loads(request.get_data(as_text=True))

            assert data["username"] == "new_username"
            assert request.status_code == 200

    def test_delete_user(self):
        with self.client as c:
            request = c.delete("/api/users/999")
            assert request.status_code == 200

    def test_create_user(self):
        with self.client as c:
            request = c.post(
                "/api/users",
                data=json.dumps(
                    {
                        "email": "test@test.com",
                        "username": "user1",
                        "password": "password",
                    }
                ),
                content_type="application/json",
            )

            data = json.loads(request.get_data(as_text=True))
            assert request.status_code == 200
            assert data["username"] == "user1"

    def test_create_user_with_invalid_email(self):
        with self.client as c:
            request = c.post(
                "/api/users",
                data=json.dumps(
                    {
                        "email": "testtest.com",
                        "username": "user1",
                        "password": "password",
                    }
                ),
                content_type="application/json",
            )
            assert request.status_code == 400

    def test_create_user_with_empty_param(self):
        with self.client as c:
            request = c.post(
                "/api/users", data=json.dumps({}), content_type="application/json"
            )
            assert request.status_code == 400


if __name__ == "__main__":
    unittest.main()
