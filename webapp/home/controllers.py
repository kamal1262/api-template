import logging

from flasgger import SwaggerView
from flask import current_app


class HealthCheckApi(SwaggerView):
    tags = ["Healthcheck"]

    def __init__(self, *args, **kwargs):
        self.logger: logging.Logger = current_app.logger

    def get(self):
        """
        To perform healthcheck
        ---
        tags:
          - Healthcheck
        responses:
          500:
            description: Healthcheck failed.
          200:
            description: Healthcheck passed.
        """
        self.logger.info("health check")
        return "OK", 200
