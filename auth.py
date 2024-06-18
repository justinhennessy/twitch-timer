import os
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

# https://console.cloud.google.com/apis/credentials -> this is where to see the Oauth2 setup

class OAuthConfig:
    def __init__(self, client_secrets_file, scopes):
        self.client_secrets_file = client_secrets_file
        self.scopes = scopes

class GoogleAuthService:
    def __init__(self, oauth_config):
        self.oauth_config = oauth_config
        self.credentials = None

    def load_credentials(self, token_path):
        if os.path.exists(token_path):
            with open(token_path, 'r') as token_file:
                self.credentials = Credentials.from_authorized_user_file(token_path, self.oauth_config.scopes)

    def save_credentials(self, token_path):
        with open(token_path, 'w') as token_file:
            token_file.write(self.credentials.to_json())

    def refresh_credentials(self):
        if self.credentials and self.credentials.expired and self.credentials.refresh_token:
            self.credentials.refresh(Request())

    def initiate_auth_flow(self, redirect_uri):
        flow = Flow.from_client_secrets_file(
            self.oauth_config.client_secrets_file, scopes=self.oauth_config.scopes,
            redirect_uri=redirect_uri
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline', include_granted_scopes='true'
        )
        return authorization_url, state

    def fetch_token(self, state, authorization_response, redirect_uri):
        flow = Flow.from_client_secrets_file(
            self.oauth_config.client_secrets_file, scopes=self.oauth_config.scopes,
            state=state, redirect_uri=redirect_uri
        )
        flow.fetch_token(authorization_response=authorization_response)
        self.credentials = flow.credentials

    def get_user_info(self):
        if self.credentials and self.credentials.valid:
            response = requests.get(
                'https://www.googleapis.com/oauth2/v1/userinfo',
                headers={'Authorization': f'Bearer {self.credentials.token}'}
            )
            if response.status_code == 200:
                return response.json()
        return None

class AuthFlowManager:
    def __init__(self, auth_service, token_path):
        self.auth_service = auth_service
        self.token_path = token_path

    def authenticate(self):
        self.auth_service.load_credentials(self.token_path)
        if not self.auth_service.credentials or not self.auth_service.credentials.valid:
            if self.auth_service.credentials and self.auth_service.credentials.expired and self.auth_service.credentials.refresh_token:
                self.auth_service.refresh_credentials()
            else:
                return None
            self.auth_service.save_credentials(self.token_path)
        return self.auth_service.credentials
