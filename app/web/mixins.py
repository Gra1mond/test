from aiohttp.abc import StreamResponse
from aiohttp.web_exceptions import HTTPForbidden, HTTPUnauthorized


class AuthRequiredMixin:
    async def _iter(self) -> StreamResponse:
        if self.request.admin is None:
            # Если была невалидная cookie, возвращаем 403, иначе 401
            if getattr(self.request, "_invalid_session", False):
                raise HTTPForbidden
            raise HTTPUnauthorized

        return await super()._iter()
