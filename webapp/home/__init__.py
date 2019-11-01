from .controllers import HealthCheckApi, HomeApi


def create_module(rest_api, **kwargs):
    rest_api.add_resource(HomeApi, "/home")
    rest_api.add_resource(HealthCheckApi, "/healthcheck")
