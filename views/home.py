import aiohttp_jinja2

from views.base import BaseView


class HomeView(BaseView):
    @aiohttp_jinja2.template('index.html.jinja2')
    async def get(self):
        return {'client_id': self.request.app['client_id']}
