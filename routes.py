from flask import Blueprint, redirect, url_for, session, send_from_directory, request
from auth import OAuthConfig, GoogleAuthService, AuthFlowManager
import os
import requests
import json

routes_bp = Blueprint('routes', __name__)

ngrok_url = "https://3aae-203-123-109-247.ngrok-free.app"

oauth_config = OAuthConfig(
    client_secrets_file='client_secrets.json',
    scopes=[
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'openid'
    ]
)
google_auth_service = GoogleAuthService(oauth_config)
auth_flow_manager = AuthFlowManager(google_auth_service, 'token.json')

@routes_bp.route('/')
def serve_login_page():
    return send_from_directory('static', 'register.html')

@routes_bp.route("/login")
def login():
    authorization_url, state = google_auth_service.initiate_auth_flow(f"{ngrok_url}/oauth2callback")
    session['state'] = state
    return redirect(authorization_url)

@routes_bp.route("/oauth2callback")
def oauth2callback():
    state = session['state']
    google_auth_service.fetch_token(state, request.url, f"{ngrok_url}/oauth2callback")
    auth_flow_manager.auth_service.save_credentials('token.json')

    user_info = google_auth_service.get_user_info()
    if user_info:
        session['email'] = user_info['email']
        session['access_token'] = google_auth_service.credentials.token

        fetch_register_url = f"{ngrok_url}/api/register"
        response = requests.post(fetch_register_url, json={"email": user_info['email']})

        try:
            response_data = response.json()
            if response.status_code == 200 and 'uuid' in response_data:
                session['uuid'] = response_data['uuid']
                return redirect(f"/personal_timer.html?uuid={response_data['uuid']}")
            else:
                return "Failed to register user", 500
        except json.JSONDecodeError as e:
            return "Failed to register user", 500

    return redirect('/register.html')

@routes_bp.route("/protected_resource")
def protected_resource():
    credentials = auth_flow_manager.authenticate()
    if not credentials:
        return redirect(url_for('login'))
    return f'Access Token: {credentials.token}'

@routes_bp.route('/register.html')
def serve_register_page():
    return send_from_directory('static', 'register.html')

@routes_bp.route('/personal_timer.html')
def serve_personal_timer_page():
    return send_from_directory('static', 'personal_timer.html')

@routes_bp.route('/timer.html')
def serve_timer_html():
    return send_from_directory('static', 'timer.html')

@routes_bp.route('/admin.html')
def serve_admin_html():
    return send_from_directory('static', 'admin.html')

@routes_bp.route('/favicon.ico')
def serve_favicon():
    return send_from_directory('static', 'favicon.ico')

