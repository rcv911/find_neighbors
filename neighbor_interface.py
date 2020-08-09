"""Интерейс позволяет запросить K ближайших соседей пользователя N в радиусе
M километров.Сгенерировать пользователей. CRUD на управление пользователями."""
from scipy.spatial import cKDTree
import logging
import namegenerator
import numpy as np
import time

log = logging.getLogger(__name__)


class FindNeighbor:

    def __init__(self, qty_users: int, const: int, radius: int, k: int):
        self.users = {}
        self.id_ = qty_users
        self.quantity = qty_users
        self.const = const
        self.radius = radius
        self.k = k
        self.tree = None

    def __repr__(self):
        return self.__class__.__name__

    def make_model(self):
        points = [(u['x'], u['y']) for id_, u in self.users.items()]
        if points:
            self.tree = cKDTree(points)

    def is_exist(self, user_id: int) -> bool:
        return user_id in self.users

    def get_len(self) -> int:
        return len(self.users)

    def get_user(self, user_id: int) -> dict:
        if not self.is_exist(user_id):
            return {'data': 'Пользователь не найден', 'status': 404}
        return self.users[user_id]

    def gen_users(self) -> bool:
        """Генерация реестра пользователей."""
        self.users = {i: {
            'id': i,
            'name': namegenerator.gen(),
            'x': np.random.random() * self.const,
            'y': np.random.random() * self.const
        } for i in range(self.quantity)}
        return True

    def create_user(self, kwargs: dict) -> dict:
        """Создание нового пользователя."""
        x = kwargs.get('x', np.random.random() * self.const)
        y = kwargs.get('y', np.random.random() * self.const)
        self.check_value(x)
        self.check_value(y)

        name = kwargs.get('name', namegenerator.gen())
        new_id = self.id_
        new_user = {
            'id': new_id,
            'name': name,
            'x': float(x),
            'y': float(y),
        }
        self.users[new_id] = new_user
        self.id_ += 1
        self.make_model()
        return self.get_user(new_id)

    def update_user(self, kwargs: dict) -> dict:
        """Обновление данных пользователя."""
        user_id = int(kwargs.get('user_id'))
        user = self.get_user(user_id)
        for col in user:
            if col in kwargs:
                self.users[user_id][col] = kwargs.get(col)
        self.make_model()
        return self.get_user(user_id)

    def delete_user(self, user_id: int) -> int:
        """Удаление пользователя."""
        if self.is_exist(user_id):
            del self.users[user_id]
            self.make_model()
        return user_id

    def get_neighbors(self, kwargs: dict) -> dict:
        """Получить соседей пользователя в заданном радиусе."""
        user_id = int(kwargs.get('user_id'))
        radius = kwargs.get('radius', self.radius)
        k_neighbor = kwargs.get('k', self.k)
        self.check_value(radius)
        self.check_value(k_neighbor)
        radius = float(radius)
        k_neighbor = float(k_neighbor)

        user = self.get_user(user_id)
        user_coordinates = [user['x'], user['y']]
        k = min(k_neighbor, self.get_len() - 1) + 1

        start = time.time()
        dist, location = self.tree.query(user_coordinates, k=k)
        if isinstance(location, int):
            dist = [dist]
            location = [location]

        index_neighbors = self.get_neighbors_in_radius(dist, location, radius)
        neighbors = [self.users[i] for i in index_neighbors]
        log.debug(f'GET NEIGHBORS {time.time() - start}')
        return {
            'user': user,
            'neighbors': neighbors
        }

    @staticmethod
    def get_neighbors_in_radius(dist: list, index: list,
                                radius: (int, float)) -> list:
        """Получить индексы соседей пользователя в заданном радиусе."""
        index_neighbors = list(zip(dist, index))[1:]
        return [index for dist, index in index_neighbors if dist <= radius]

    @staticmethod
    def check_value(value: (str, int, float)) -> (None, dict):
        if isinstance(value, str) and not value.replace('.', '', 1).isdigit():
            return {
                'data': f'Параметр {value} должен быть числом',
                'status': 406
            }
