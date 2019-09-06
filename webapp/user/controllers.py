import logging

from flasgger import SwaggerView, Schema, fields
from flask import request, current_app
from flask_restplus import abort
from marshmallow import validate

from .models import User
from .services import (
    UserService,
    AddUserRequest,
    DeleteUserRequest,
    GetUserRequest,
    UpdateUserRequest,
)


class UserSchema(Schema):
    username = fields.Str()
    id = fields.Int()
    email = fields.Email()


class CreateUserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    email = fields.Email(required=True)


class UpdateUserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    email = fields.Email(required=True)


class UserListApi(SwaggerView):
    tags = ["Users"]
    definitions = {"UserSchema": UserSchema, "CreateUserSchema": CreateUserSchema}

    def __init__(self, *args, **kwargs):
        self.logger: logging.Logger = current_app.logger
        self.user_service = UserService()

    def get(self):
        """
        To get a list of users
        ---
        responses:
          500:
            description: Error User {ID} does not exist.
          200:
            description: List of users
            type: array
            items:
              schema:
                $ref: '#/definitions/UserSchema'
        """
        users_data = self.user_service.list_all()
        return UserSchema(many=True).dump(users_data).data

    def post(self):
        """
        To create new user
        ---
        requestBody:
          description: Create User Data
          required: true
          content:
            application/json:
              schema:
                $ref: '#/definitions/CreateUserSchema'
        responses:
          500:
            description: Error Internal Server Error.
          200:
            description: User object
            content:
              application/json:
                schema:
                  $ref: '#/definitions/UserSchema'
        """
        user_schema: Schema = CreateUserSchema()
        result = user_schema.load(request.get_json())
        if result.errors:
            abort(400, str(result.errors))
        user_data = result.data
        user: User = self.user_service.add_user(AddUserRequest(user_data))

        return UserSchema().dump(user).data


class UserApi(SwaggerView):
    tags = ["Users"]
    definitions = {"UserSchema": UserSchema, "UpdateUserSchema": UpdateUserSchema}

    def __init__(self, *args, **kwargs):
        self.logger: logging.Logger = current_app.logger
        self.user_service = UserService()

    def get(self, user_id: int):
        """
        To get a user
        ---
        tags:
          - Users
        parameters:
          - name: user_id
            in: path
            description: User ID
            required: true
            schema:
              type: integer
              format: int32
        responses:
          404:
            description: Error User {ID} does not exist.
          200:
            description: User object
            content:
              application/json:
                schema:
                  $ref: '#/definitions/UserSchema'
        """
        user: User = self.user_service.find_by_id(GetUserRequest({"user_id": user_id}))

        return UserSchema().dump(user).data

    def put(self, user_id: int):
        """
        To update a user
        ---
        tags:
          - Users
        parameters:
          - name: user_id
            in: path
            description: User ID
            required: true
            schema:
              type: integer
              format: int32
        requestBody:
          description: Update User Data
          required: true
          content:
            application/json:
              schema:
                $ref: '#/definitions/UpdateUserSchema'
        responses:
          404:
            description: Error User {ID} does not exist.
          200:
            description: User Object
            content:
              application/json:
                schema:
                  $ref: '#/definitions/UserSchema'
        """
        user_schema: Schema = UpdateUserSchema()
        result = user_schema.load(request.get_json())
        if result.errors:
            abort(400, str(result.errors))
        user_data = result.data
        user_data["user_id"] = user_id
        user: User = self.user_service.update_user(UpdateUserRequest(user_data))
        return UserSchema().dump(user).data

    def delete(self, user_id: int):
        """
        To delete a user
        ---
        tags:
          - Users
        parameters:
          - name: user_id
            in: path
            description: User ID
            required: true
            schema:
              type: integer
              format: int32
        responses:
          404:
            description: Error User {ID} does not exist.
          200:
            description: User Object
            content:
              application/json:
                schema:
                  $ref: '#/definitions/UserSchema'
        """
        user: User = self.user_service.delete_user(
            DeleteUserRequest({"user_id": user_id})
        )
        return UserSchema().dump(user).data
