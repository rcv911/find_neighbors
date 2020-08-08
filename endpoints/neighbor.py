from typing import List
from aiohttp.web import Request
from aiohttp.web_response import Response
from aiohttp_rest_api import AioHTTPRestEndpoint
from aiohttp_rest_api.responses import respond_with_json
from api import make_response
import logging

log = logging.getLogger(__name__)


class NeighborEndpoint(AioHTTPRestEndpoint):

    def connected_routes(self) -> List[str]:
        """"""
        return [
            '/neighbor'
        ]

    @staticmethod
    def get_interface(request: Request):
        user_id = request.query.get('user_id')
        if not user_id:
            return respond_with_json(make_response('Требуется user_id', 400))
        elif not user_id.isdigit():
            return respond_with_json(make_response(
                'user_id должен быть числом', 406))

        return request.app['find_neighbor']

    async def get(self, request: Request) -> Response:
        """
        GET метод /v1/neighbor получить K ближайших соседей пользователя N в
        радиусе M."""
        interface = self.get_interface(request)
        data = interface.get_neighbors(request.query)
        # TODO смореть готово ли приложение к работе и сколько по времени
        #  это заняло
        return respond_with_json(make_response(data, 200))
