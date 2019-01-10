from aiohttp.web import View, Response


class LoginView(View):
    """The handler for the streaming web-cam server."""
    async def get(self):
        return Response(text="Hello, World!")

    async def post(self):
        return Response(text="Hello, World!")
