from typing import List
from aiohttp.web import Request
from aiohttp.web_response import Response
from aiohttp_rest_api import AioHTTPRestEndpoint
from aiohttp_rest_api.responses import respond_with_json
from api import make_response
import logging

log = logging.getLogger(__name__)


class EntryEndpoint(AioHTTPRestEndpoint):

    def connected_routes(self) -> List[str]:
        """"""
        return [
            '/'
        ]

    async def get(self, request: Request) -> Response:
        """GET метод /v1/ Получение количества пользователей."""
        interface = request.app['find_neighbor']
        return respond_with_json(make_response(
                f'Количество пользователей: {interface.get_len()}', 200)
            )
