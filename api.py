"""Настройка и запуск приложения."""
import time
from concurrent.futures.thread import ThreadPoolExecutor

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
    app = web.Application()
    interface = init_interface_find_neighbor(config.get('app'))
    log.debug(f'app_interface {interface}')

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
    log.debug(f'CONFIG {config}')
    qty_users = config.get('qty_users', 1000)
    const = config.get('const', 100)
    radius = config.get('radius', 50)
    k = config.get('k', 10_000)
    log.debug(f'QTY USERS {qty_users}')
    return FindNeighbor(qty_users, const, radius, k)


def generate_users(interface: FindNeighbor):
    """Генерация реестра пользователей.  CPU bound задача."""
    start = time.time()
    interface.gen_users()
    log.debug(f'GEN USERS {time.time() - start} sec')
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

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as pool:
        _ = loop.run_in_executor(pool, generate_users(app['find_neighbor']))

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
