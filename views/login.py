import aiohttp_jinja2
from aiohttp.web import View


class LoginView(View):
    @aiohttp_jinja2.template('login.html.jinja2')
    async def get(self):
        return {
            'client_id': self.request.app['client_id'],
            'domain': self.request.app['domain'],
            'port': self.request.app['port']
        }
