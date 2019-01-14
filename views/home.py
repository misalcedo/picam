import aiohttp_jinja2
from aiohttp.web import HTTPFound
from aiohttp_security import check_permission, is_anonymous

from auth.permissions import HOME
from views.base import BaseView


class HomeView(BaseView):
    @aiohttp_jinja2.template('index.html.jinja2')
    async def get(self):
        if await is_anonymous(self.request):
            raise HTTPFound(self.request.app.router['sign_in'].url_for())

        await check_permission(self.request, HOME, self.request.app)

        return {
            'sign_out': self.request.app.router['sign_out'].url_for(),
            'clips': self.request.app.router['clips'].url_for(filename='/')}

