from .controllers import HealthCheckApi


def create_module(rest_api, **kwargs):
    rest_api.add_resource(HealthCheckApi, "/healthcheck")
