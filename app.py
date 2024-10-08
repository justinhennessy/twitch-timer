from flask import Flask
from flask_cors import CORS
from routes import routes_bp
from routes_api import api_bp
from backend_functions import load_existing_timers, get_redis_client

import os
import time

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.secret_key = os.urandom(24)

    # Ensure Redis connection is established
    redis_client = get_redis_client()

    # Register Blueprints
    app.register_blueprint(routes_bp)
    app.register_blueprint(api_bp)

    # Load existing timers
    load_existing_timers()

    return app

if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app = create_app()
    app.run(host='0.0.0.0', port=5001, debug=True)
