from flask import Flask
from routes import routes_bp
from routes_api import api_bp
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Register Blueprints
app.register_blueprint(routes_bp)
app.register_blueprint(api_bp)

if __name__ == "__main__":
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.run(host='0.0.0.0', port=5001, debug=True)
