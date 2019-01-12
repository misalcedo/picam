from aiohttp.web import View


class BaseView(View):
    def __iter__(self):
        """See https://github.com/aio-libs/aiohttp-debugtoolbar/issues/207"""
        return self._iter().__await__()
