import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    APP_TITLE = os.environ.get("TITLE", default="API")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_RECYCLE = int(os.environ.get("SQLALCHEMY_POOL_RECYCLE", 3600))
    LOG_FORMAT = "[%(asctime)s] %(module)s - %(levelname)s: %(message)s"
    LOG_LEVEL = os.environ.get("LOG_LEVEL", default="INFO")
    ERROR_404_HELP = False
    SWAGGER = {
        "title": os.environ.get("TITLE", default="API"),
        "version": os.environ.get("VERSION", default="Undefined"),
        "uiversion": 3,
        "openapi": "3.0.2",
        "specs": [{"endpoint": "apispec", "route": "/apispec.json"}],
    }
    XRAY = {
        "enabled": (os.environ.get("XRAY_ENABLED", "False") or "False").lower()
        == "true",
        "daemon_url": os.environ.get("XRAY_DAEMON_URL", default="127.0.0.1:2000")
        or "127.0.0.1:2000",
        "inspect_sql_query": os.environ.get("XRAY_INSPECT_QUERY", "False"),
    }
    JWT_ACCESS_TOKEN_EXPIRES = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI")
    MESSAGE_PRODUCER = os.environ.get("PRODUCER_TYPE")
    MESSAGE_TOPICS = os.environ.get("PRODUCER_TOPICS", "").split(",")
    TOPIC_CONSUMERS = os.environ.get("TOPIC_CONSUMERS", "").split(",")
    TOPIC_INTERVAL = int(os.environ.get("TOPIC_INTERVAL", "30"))


class ProductionConfig(Config):
    ENV = "production"


class DevelopmentConfig(Config):
    ENV = "development"


class TestConfig(Config):
    ENV = "test"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "TeStKey"
