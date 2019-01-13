import logging

import google_auth_oauthlib.flow
from aiohttp.web import HTTPFound, HTTPUnauthorized
from aiohttp_security import remember
from aiohttp_session import get_session
from google.auth.transport import requests
from google.oauth2 import id_token

from views.base import BaseView

ISSUERS = ['accounts.google.com', 'https://accounts.google.com']


class AuthView(BaseView):
    async def get(self):
        session = await get_session(self.request)

        if self.request.query.getone('state') != session['state']:
            raise HTTPUnauthorized()

        state = session['state']
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('resources/client_secret.json', scopes=[
            'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/plus.me'], state=state)

        path = self.request.app.router['auth'].url_for()
        flow.redirect_uri = self.request.url.join(path).human_repr()

        authorization_response = self.request.url.human_repr()
        flow.fetch_token(authorization_response=authorization_response)

        credentials = flow.credentials
        session['credentials'] = {
            'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'id_token': credentials.id_token,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

        user = id_token.verify_oauth2_token(credentials.id_token, requests.Request(), self.request.app['client_id'])

        if user['iss'] not in ISSUERS:
            logging.info('Wrong issuer: %s.', user['iss'])
            raise HTTPUnauthorized()

        session['user'] = user

        response = HTTPFound("/")
        await remember(self.request, response, user['email'])
        raise response
