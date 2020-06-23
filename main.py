import os

from flasgger import Swagger
from flask_cors import CORS

from webapp import create_app

from diagnostics_endpoint import Diagnostics

env = os.environ.get("FLASK_ENV", "development")
app = create_app("config.%sConfig" % env.capitalize())

swagger = Swagger(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})



application_endpoints = [
    {"name": "API Template", "endpoint": "/heartbeat"}
]

app = Flask(__name__)
Diagnostics.render(app, application_endpoints)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
