from schematics.models import Model
from schematics.types import StringType, EmailType, IntType

from .models import User
from .. import db
from ..common.errors import UserNotFoundException


class AddUserRequest(Model):
    username = StringType(required=True)
    password = StringType(required=True)
    email = EmailType(required=True)


class DeleteUserRequest(Model):
    user_id = IntType(required=True)


class GetUserRequest(Model):
    user_id = IntType(required=True)


class UpdateUserRequest(Model):
    user_id = IntType(required=True)
    username = StringType(required=True)
    password = StringType()
    email = EmailType()


class UserService:
    def __init__(self):
        self.db = db

    def list_all(self):
        return self.db.session.query(User).all()

    def find_by_id(self, request: GetUserRequest):
        request.validate()
        user: User = self.__get_user(request.user_id)
        if user is None:
            raise UserNotFoundException("User not found")
        return user

    def add_user(self, request: AddUserRequest):
        request.validate()
        user: User = User(
            username=request.username, email=request.email, password=request.password
        )
        self.db.session.add(user)
        self.db.session.commit()
        return user

    def update_user(self, request: UpdateUserRequest):
        request.validate()
        user: User = self.__get_user(request.user_id)
        if user is None:
            raise UserNotFoundException("User not found")
        user.username = request.username
        self.db.session.commit()
        return user

    def delete_user(self, request: DeleteUserRequest):
        request.validate()
        user: User = self.__get_user(request.user_id)
        if user is None:
            raise UserNotFoundException("User not found")
        self.db.session.delete(user)
        self.db.session.commit()
        return user

    def __get_user(self, user_id: int) -> User:
        return self.db.session.query(User).get(user_id)
