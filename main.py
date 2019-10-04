import os

from flasgger import Swagger
from flask_cors import CORS

from webapp import create_app

print(os.environ)
env = os.environ.get("FLASK_ENV", "development")
app = create_app("config.%sConfig" % env.capitalize())

swagger = Swagger(app)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

if __name__ == "__main__":
    app.run(host="0.0.0.0")
