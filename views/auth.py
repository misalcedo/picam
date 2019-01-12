from aiohttp.web import View, HTTPFound


class AuthView(View):
    async def get(self):
        # TODO: verify user's e-mail is in authorized users.
        raise HTTPFound("/")
