import google.oauth2.credentials
import google_auth_oauthlib.flow


class GoogleAuth:
    """An OAuth implementation for the Google Auth APIs."""
    def __init__(self, secrets_path, redirect_uri):
        self.secrets_path = secrets_path
        self.redirect_uri = redirect_uri

    def authenticate(self):
        # Use the client_secret.json file to identify the application requesting
        # authorization. The client ID (from that file) and access scopes are required.
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
                   self.secrets_path,
                   state="dummy-value", # TODO: add state nonce. See https://developers.google.com/api-client-library/python/auth/web-app
                   scope=["https://www.googleapis.com/auth/userinfo.email"])

        # Indicate where the API server will redirect the user after the user completes
        # the authorization flow. The redirect URI is required.
        flow.redirect_uri = self.redirect_uri

        # Generate URL for request to Google's OAuth 2.0 server.
        # Use kwargs to set optional request parameters.
        # Enable incremental authorization. Recommended as a best practice.
        authorization_url, state = flow.authorization_url(include_granted_scopes='true')
