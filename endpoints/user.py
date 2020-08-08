from typing import List
from aiohttp.web import Request
from aiohttp.web_response import Response
from aiohttp_rest_api import AioHTTPRestEndpoint
from aiohttp_rest_api.responses import respond_with_json
from api import make_response
import logging

log = logging.getLogger(__name__)


class UserEndpoint(AioHTTPRestEndpoint):

    def connected_routes(self) -> List[str]:
        """"""
        return [
            '/user'
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
        """GET метод /v1/user получение пользователя по идентификатору."""
        interface = self.get_interface(request)
        data = interface.get_user(int(request.query.get('user_id')))
        return respond_with_json(data)

    async def post(self, request: Request) -> Response:
        """POST метод /v1/user создание новго пользователя."""
        interface = request.app['find_neighbor']
        data = interface.create_user(request.query)
        return respond_with_json(data)

    async def put(self, request: Request) -> Response:
        """PUT метод /v1/user обновление данных пользователя по
        идентификатору."""
        interface = self.get_interface(request)
        data = interface.update_user(request.query)
        return respond_with_json(data)

    async def delete(self, request: Request) -> Response:
        """DELETE метод /v1/user удаление пользователя по идентификатору."""
        interface = self.get_interface(request)
        user_id = interface.delete_user(int(request.query.get('user_id')))
        return respond_with_json(make_response(f'Удалён пользователь с id '
                                               f'{user_id}', 200))
