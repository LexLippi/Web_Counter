import os
import aiosqlite
import datetime

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
SELECT_COUNT = ('SELECT COUNT(*) FROM stat WHERE site = ? '
                'AND date <= ? AND date >= ?')
SELECT_UNIQUE = ('SELECT COUNT(DISTINCT client) FROM stat WHERE site = ? '
                 'AND date <= ? AND date >= ?')
SELECT_ALL_UNIQUE = 'SELECT COUNT(DISTINCT client) FROM stat WHERE site = ?'


class Database:
    @classmethod
    async def init(cls, db_name):
        """
        Проверка имеется ли база данных с таким названием, если нет,
        то она создается, если есть, то мы присоединяемся к ней.
        """
        self = cls()
        if not os.path.isfile(db_name):
            await self.create_db(db_name)
        self.conn = await aiosqlite.connect(db_name)
        return self

    @staticmethod
    async def create_db(db_name):
        """
        Создание базы данных с необходимыми столбцами.
        """
        async with aiosqlite.connect(db_name) as conn:
            await conn.execute(
                """CREATE TABLE stat (
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                site TEXT NOT NULL,
                client TEXT NOT NULL,
                date TEXT NOT NULL)
                """)
            await conn.commit()

    async def get_stats(self, site_id):
        """
        Функция, получающая статистику из базы данных. Она возвращает лист из
        словаря с количеством посещений за день, за месяц, за год и количество
        уникальных посещений за месяц, за год, за все время, прошедшее со
        старта приложения.
        """
        date = datetime.datetime.now()
        day_ago_date = (date - datetime.timedelta(days=1)).strftime(
            DATE_FORMAT)
        month_ago_date = (date - datetime.timedelta(weeks=4)).strftime(
            DATE_FORMAT)
        year_ago_date = (date - datetime.timedelta(days=365)).strftime(
            DATE_FORMAT)
        date = date.strftime(DATE_FORMAT)
        res = {'day': await self.get_stats_from_db(
            SELECT_COUNT, site_id, date, day_ago_date),
               'month': await self.get_stats_from_db(
            SELECT_COUNT, site_id, date, month_ago_date),
               'year': await self.get_stats_from_db(
            SELECT_COUNT, site_id, date, year_ago_date)}
        unique_res = {'month': await self.get_stats_from_db(
            SELECT_UNIQUE, site_id, date, month_ago_date),
                      'year': await self.get_stats_from_db(
            SELECT_UNIQUE, site_id, date, year_ago_date),
                      'total': await self.get_stats_from_db(
            SELECT_ALL_UNIQUE, site_id)}
        return {'all': res, 'unique': unique_res}

    async def get_stats_from_db(self, text, site, date=None, past_date=None):
        """
        Функцтя, которая по заданным параметрам возвращает из базы данных
        целочисленное значение, количество посещений данного сайта
        в зависимотси от параметров
        """
        if date is None and past_date is None:
            async with self.conn.execute(text, [site]) as cursor:
                return (await cursor.fetchone())[0]
        async with self.conn.execute(text, [site, date, past_date]) as cursor:
            return (await cursor.fetchone())[0]

    async def add_stats(self, site_id, client, date: str):
        """
        Функция, которая добавляет статистику посещений в базу данных.
        Статистика состоит из трех строковых параметров: адрес сайта,
        ip-адрес клиента, дата в определенном формате.
        """
        await self.conn.execute(
            'INSERT INTO stat VALUES (?, ?, ?, ?)',
            [None, site_id, client, date])
        await self.conn.commit()

    async def close(self):
        """
        Функция, эмулирующая корректное закрытие соединения с базой данных.
        """
        await self.conn.close()
