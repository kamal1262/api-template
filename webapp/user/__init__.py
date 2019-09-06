from .controllers import UserApi, UserListApi


def create_module(rest_api, **kwargs):
    rest_api.add_resource(UserListApi, "/api/users")
    rest_api.add_resource(UserApi, "/api/users/<int:user_id>")
