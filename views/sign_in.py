import hashlib
import os

import aiohttp_jinja2
import google_auth_oauthlib.flow
from aiohttp.web import HTTPFound
from aiohttp_session import get_session

from views.base import BaseView


class SignInView(BaseView):
    @aiohttp_jinja2.template('sign_in.html.jinja2')
    async def get(self):
        path = self.request.app.router['auth'].url_for()

        return {'redirect_uri': self.request.url.join(path).human_repr()}

    async def post(self):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file('resources/client_secret.json', scopes=[
            'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/plus.me'])

        session = await get_session(self.request)
        session['state'] = hashlib.sha256(os.urandom(1024)).hexdigest()

        path = self.request.app.router['auth'].url_for()
        flow.redirect_uri = self.request.url.join(path).human_repr()

        authorization_url, state = flow.authorization_url(state=session['state'], access_type='offline',
                                                          include_granted_scopes='true')

        raise HTTPFound(authorization_url)
