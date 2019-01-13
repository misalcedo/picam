import logging

from aiohttp import ClientSession
from aiohttp.web import HTTPFound, Response
from aiohttp_security import forget, is_anonymous, authorized_userid
from aiohttp_session import get_session
from aiojobs.aiohttp import spawn

from views.base import BaseView


class SignOutView(BaseView):
    async def post(self):
        if await is_anonymous(self.request):
            return Response()

        await spawn(self.request, self.revoke_token())

        response = HTTPFound(self.request.app.router['sign_in'].url_for())
        await forget(self.request, response)
        raise response

    async def revoke_token(self):
        session = await get_session(self.request)

        async with ClientSession() as client:
            async with client.post('https://accounts.google.com/o/oauth2/revoke',
                                   data={'token': session['credentials']['token']},
                                   headers={'content-type': 'application/x-www-form-urlencoded'}) as revoke_response:
                logging.info(
                    "Received %d status to revoke the token of %s",
                    revoke_response.status,
                    await authorized_userid(self.request))
