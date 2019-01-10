from aiohttp.web import View, Response


class HomeView(View):
    """The handler for the streaming web-cam server."""
    async def get(self):
        return Response(text="Hello, World!")

