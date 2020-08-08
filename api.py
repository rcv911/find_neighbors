"""Настройка и запуск приложения."""
import time

from aiohttp import web
from aiohttp.web import Application
from aiohttp_rest_api.loader import \
    load_and_connect_all_endpoints_from_folder
from neighbor_interface import FindNeighbor
import asyncio
import logging
import pathlib
import pytoml as toml
import os


BASE_DIR = pathlib.Path(__file__).parent.parent
PACKAGE_NAME = 'app'
log = logging.getLogger(__name__)


def make_response(data: (str, dict), status: int = 500) -> dict:
    return {
        'data': data,
        'status': status
    }


def load_config(config_path: str) -> dict:
    """Загрузка конфигурации приложения."""
    with open(f'{os.getcwd()}{config_path}') as f:
        conf = toml.load(f)
    return conf


def init_app(config: dict) -> Application:
    """Инициализация web приложения."""
    loop = asyncio.get_event_loop()
    app = web.Application()
    interface = init_interface_find_neighbor(config)
    log.debug(f'app_interface {interface}')
    loop.create_task(generate_users(interface))

    app['config'] = config
    app['find_neighbor'] = interface

    load_and_connect_all_endpoints_from_folder(
        path='{0}/{1}'.format(os.path.dirname(os.path.realpath(__file__)),
                              'endpoints'),
        app=app,
        version_prefix='v1'
    )

    log.debug(app['config'])
    return app


def init_interface_find_neighbor(config: dict):
    """Инициаллизация интерфейса FindNeighbor."""
    qty_users = config.get('qty_users', 1000)
    const = config.get('const', 100)
    radius = config.get('radius', 50)
    k = config.get('k', 10)
    return FindNeighbor(qty_users, const, radius, k)


async def generate_users(interface: FindNeighbor):
    """Генерация реестра пользователей."""
    start = time.time()
    interface.gen_users()
    log.debug(f'GEN USERS {time.time() - start} sec')
    log.debug(f'USER SIZE {interface.get_size()}')
    start = time.time()
    interface.make_model()
    log.debug(f'MAKE MODEL {time.time() - start} sec')


def main(config_path: str):
    """Запуск REST API."""
    logging.basicConfig(level=logging.DEBUG)
    log.debug(f'config_path - {config_path}')

    config = load_config(config_path)
    app = init_app(config)
    app_config = config.get('app', {})

    web.run_app(app, port=app_config.get('port', 2020))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", help="Provide path to config file")
    args = parser.parse_args()

    if args.config:
        main(args.config)
    else:
        parser.print_help()
