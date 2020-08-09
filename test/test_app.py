import time
from unittest import TestCase
from timeit import timeit
from neighbor_interface import FindNeighbor


class FindNeighborTestCase(TestCase):

    def setUp(self):
        self.qty_users = 0
        self.const = 10
        self.radius = 0
        self.k = 0
        self.interface = FindNeighbor(self.qty_users, self.const, self.radius,
                                      self.k)


class TestCRUD(FindNeighborTestCase):

    def test_get(self):
        user_id = 0
        self.interface.gen_users()
        self.assertTrue(self.interface.is_exist(user_id))
        self.assertFalse(self.interface.is_exist(-1))
        self.assertFalse(self.interface.is_exist(10_000))
        user = self.interface.get_user(user_id)
        self.assertIsInstance(user.get('name'), str)
        self.assertIsInstance(user.get('x'), float)
        self.assertIsInstance(user.get('y'), float)

    def test_create(self):
        user = self.interface.create_user({'name': 'test', 'x': 1.0, 'y': 1.0})
        self.assertTrue(self.interface.is_exist(user.get('id')))
        self.assertDictEqual({
            'id': user.get('id'), 'name': 'test', 'x': 1.0, 'y': 1.0
        }, self.interface.get_user(user.get('id')))

    def test_update(self):
        created = self.interface.create_user({
            'name': 'created', 'x': 1.0, 'y': 1.0
        })
        self.assertTrue(self.interface.is_exist(created.get('id')))
        updated = self.interface.update_user({
            'user_id': created.get('id'), 'name': 'updated', 'x': 2.0, 'y': 3.5
        })
        self.assertDictEqual({
            'id': updated.get('id'), 'name': 'updated', 'x': 2.0, 'y': 3.5
        }, self.interface.get_user(updated.get('id')))

    def test_delete(self):
        created = self.interface.create_user({
            'name': 'created', 'x': 1.0, 'y': 1.0
        })
        self.assertTrue(self.interface.is_exist(created.get('id')))
        deleted_id = self.interface.delete_user(created.get('id'))
        self.assertIsInstance(deleted_id, int)


class TestFindNeighbor(FindNeighborTestCase):

    def test_neighbor_zero_radius(self):
        self.interface.create_user({'name': 'user', 'x': 0.0, 'y': 0.0})
        self.interface.create_user({'name': 'neighbor_1', 'x': 0.5, 'y': 0.0})
        self.interface.create_user({'name': 'neighbor_2', 'x': 0.0, 'y': 0.5})
        user = self.interface.get_user(self.qty_users)
        self.assertEqual('user', user['name'])
        data = self.interface.get_neighbors({
            'user_id': user.get('id'), 'radius': 0.0, 'k': 5
        })
        self.assertEqual(0, len(data['neighbors']))

    def test_neighbor_in_radius(self):
        self.interface.create_user({'name': 'user', 'x': 0.0, 'y': 0.0})
        self.interface.create_user({'name': 'neighbor_1', 'x': 0.5, 'y': 0.0})
        self.interface.create_user({'name': 'neighbor_2', 'x': 0.0, 'y': 0.5})
        self.interface.create_user({'name': 'neighbor_3', 'x': 2.0, 'y': 2.0})
        user = self.interface.get_user(self.qty_users)
        self.assertEqual('user', user['name'])
        data = self.interface.get_neighbors({
            'user_id': user.get('id'), 'radius': 1.0, 'k': 5
        })
        self.assertTrue(data['neighbors'])
        self.assertEqual(2, len(data['neighbors']))
        self.assertEqual('neighbor_1', data['neighbors'][1]['name'])
        self.assertEqual('neighbor_2', data['neighbors'][0]['name'])


class TestPerformance(FindNeighborTestCase):

    def test_performance(self):
        qty_runs = 1000
        for qty_users in (100, 1_000, 10_000, 100_000, 1_000_000, 10_000_000):
            self.interface = FindNeighbor(qty_users, self.const, self.radius,
                                          self.k)
            print('Gen users...')
            start = time.time()
            self.interface.gen_users()
            print(f'Gen users is done for {round(time.time() - start, 3)} sec')
            print('Make tree...')
            start = time.time()
            self.interface.make_model()
            print(f'Make tree is done for {round(time.time() - start, 3)} sec')
            print('Get neighbors...')
            result = timeit(lambda: self.interface.get_neighbors({
                'user_id': 0, 'radius': 50.0, 'k': 100
            }), number=qty_runs)
            print(f'{qty_users} items: get_neighbors takes {round(result, 3)} '
                  f'for {qty_runs} runs\n')
