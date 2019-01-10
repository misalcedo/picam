from aiohttp.web import View
import aiohttp_jinja2


class HomeView(View):
    @aiohttp_jinja2.template('index.html.jinja2')
    async def get(self):
        return {'client_id': self.request.app['client_id']}
