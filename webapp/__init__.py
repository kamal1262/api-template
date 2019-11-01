import logging
import os

from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware
from aws_xray_sdk.ext.flask_sqlalchemy.query import XRayFlaskSqlAlchemy
from flask import Flask, current_app
from flask_migrate import Migrate
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy

from .messagequeue.in_memory_consumer import InMemoryConsumer  # noqa: F401
from .messagequeue.in_memory_publisher import InMemoryPublisher  # noqa: F401
from .messagequeue.sqs_consumer import SQSConsumer  # noqa: F401
from .messagequeue.sqs_publisher import SQSPublisher  # noqa: F401

db = (
    XRayFlaskSqlAlchemy()
    if (
        os.environ.get("XRAY_ENABLED", "False") == "True"
        and os.environ.get("XRAY_INSPECT_QUERY", "False") == "True"
    )
    else SQLAlchemy()
)
migrate = Migrate()


def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/
    Arguments:
        object_name: the python path of the config object,
                     e.g. project.config.ProdConfig
    """
    app = Flask(__name__)
    app.config.from_object(object_name)

    app.app_context().push()
    current_app.logger = create_logger(
        app.config["LOG_LEVEL"], app.config["LOG_FORMAT"]
    )

    current_app.message_publisher = create_message_publisher(app)

    init_message_consumer(app)

    db.init_app(app)

    from .user.models import User  # noqa: F401

    migrate.init_app(app, db)

    from .user import create_module as user_create_module
    from .home import create_module as home_create_module
    from .errors import create_module as error_create_module

    rest_api: Api = Api(doc=False)

    user_create_module(rest_api)
    home_create_module(rest_api)
    error_create_module(rest_api, app=app)

    rest_api.init_app(app)

    xray_recorder.configure(
        service=app.config["APP_TITLE"],
        daemon_address=app.config["XRAY"]["daemon_url"],
        sampling_rules={
            "version": 2,
            "rules": [
                {
                    "description": "Healthcheck",
                    "host": "*",
                    "http_method": "GET",
                    "url_path": "/healthcheck*",
                    "fixed_target": 0,
                    "rate": 0.0,
                }
            ],
            "default": {"fixed_target": 1, "rate": 0.1},
        },
    )

    XRayMiddleware(app, xray_recorder)

    return app


def init_message_consumer(app):
    if app.config["TOPIC_CONSUMERS"]:
        for item in app.config["TOPIC_CONSUMERS"]:
            if item:
                config = item.split(":")
                MessageConsumer = globals()[config[1]]
                MessageConsumer(app, config[0])


def create_message_publisher(app):
    if app.config["MESSAGE_PUBLISHER"]:
        MessagePublisher = globals()[app.config["MESSAGE_PUBLISHER"]]
        message_publisher = MessagePublisher(app)

        return message_publisher
    else:
        return None


def create_logger(log_level: int, log_format: str) -> logging.Logger:
    """
    A function to create custom logger for application usage,
    this logger will NOT share the same configuration as the default flask logger.
    :param log_level: the log level, refer to logging class for the options available
    :param log_format: the format of the log
    :return: logger
    """
    logger = logging.getLogger("app-logger")

    logger_handler: logging.Handler = logging.StreamHandler()
    logger_handler.setFormatter(logging.Formatter(log_format))

    logger.setLevel(log_level)

    logger.addHandler(logger_handler)
    logging.getLogger("werkzeug").addHandler(logger_handler)

    return logger
