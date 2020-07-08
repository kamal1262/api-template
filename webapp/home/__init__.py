from .controllers import HomeApi


def create_module(rest_api, **kwargs):
    rest_api.add_resource(HomeApi, "/home")
