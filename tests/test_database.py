from project.database import Database
from aiounittest import AsyncTestCase
import unittest
import asyncio


async def create_db(database):
    await database.add_stats('vk.com', '192.168.1.1', '2019-11-17 17:18:24')
    await database.add_stats(
        'google.com', '192.168.15.35', '2019-12-17 17:18:24')
    await database.add_stats('ya.ru', '192.1.1.1', '2019-10-17 17:18:24')
    await database.add_stats('vk.com', '12.18.1.1', '2019-09-17 17:18:24')
    await database.add_stats('sports.ru', '1.1.1.1', '2019-08-17 17:18:24')


class TestDatabase(AsyncTestCase):
    def setUp(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.database = asyncio.get_event_loop().run_until_complete(
            Database.init('test.db'))
        asyncio.get_event_loop().run_until_complete(
            asyncio.gather(create_db(self.database)))

    def test_get_correct_types_from_add_posts(self):
        result = asyncio.get_event_loop().run_until_complete(
            self.database.get_stats('sports.ru'))
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result['all'], dict)
        self.assertIsInstance(result['unique'], dict)
        self.assertIsInstance(result['all']['day'], int)
        self.assertIsInstance(result['all']['month'], int)
        self.assertIsInstance(result['all']['year'], int)
        self.assertIsInstance(result['unique']['month'], int)
        self.assertIsInstance(result['unique']['year'], int)
        self.assertIsInstance(result['unique']['total'], int)

    def test_get_correct_stats(self):
        expected_result = {'all': {'day': 0, 'month': 0, 'year': 1},
                           'unique': {'month': 0, 'year': 1, 'total': 1}}
        result = asyncio.get_event_loop().run_until_complete(
            self.database.get_stats('sports.ru'))
        self.assertDictEqual(expected_result, result)

    def tearDown(self):
        asyncio.get_event_loop().run_until_complete(self.database.close())


if __name__ == '__main__':
    unittest.main()
