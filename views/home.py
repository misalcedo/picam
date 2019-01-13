import aiohttp_jinja2

from views.base import BaseView
from aiohttp_security import check_permission, is_anonymous
from auth.permissions import HOME
from aiohttp.web import HTTPFound


class HomeView(BaseView):
    @aiohttp_jinja2.template('index.html.jinja2')
    async def get(self):
        if await is_anonymous(self.request):
            raise HTTPFound(self.request.app.router['login'].url_for())

        await check_permission(self.request, HOME, self.request.app)

        return {'client_id': self.request.app['client_id']}
