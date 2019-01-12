from aiohttp.web import View, HTTPFound


class AuthView(View):
    async def get(self):
        raise HTTPFound("/")
