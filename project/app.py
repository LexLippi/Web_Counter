from aiohttp import web
from project.database import Database
import datetime
from project.imager import (get_bytes_from_image, get_default_image,
                            create_image)
import uuid


class App:
    def __init__(self, db='count_visitors.db'):
        self.db = db
        self.IMAGE = get_bytes_from_image(get_default_image())

    async def get_stats(self, request):
        """
        Функция, которая возвращает статистику посещений из базы данных.
        Если при получении статистики произошла ошибка, то возвращается
        ошибочное сообщение.
        """
        try:
            assert isinstance(self.db, Database)
            data = request.query['site']
            type_request = request.query['type']
            stats = (await self.db.get_stats(data))
            if type_request == 'pic':
                img = create_image(stats)
                img_bytes = get_bytes_from_image(img)
                resp = web.StreamResponse()
                return await self.create_response_with_image(
                    resp, request, img_bytes)
            else:
                return web.json_response(stats)
        except Exception as e:
            response_obj = {'status': 'failed', 'reason': str(e)}
            return web.json_response(response_obj, status=500)

    async def get_picture(self, request):
        assert isinstance(self.db, Database)
        try:
            data = request.query['id']
            print(request.cookies)
            resp = web.StreamResponse()
            if 'data' not in request.cookies:
                unique_client = str(uuid.uuid4())
                resp.set_cookie('data', unique_client)
            else:
                unique_client = request.cookies['data']
            date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            await self.db.add_stats(data, unique_client, date)
            return await self.create_response_with_image(
                resp, request, self.IMAGE)
        except Exception as e:
            response_obj = {'status': 'failed', 'reason': str(e)}
            return web.json_response(response_obj, status=500)

    @staticmethod
    async def create_response_with_image(resp, request, image):
        resp.content_type = 'image/png'
        resp.headers['X-UA-COMPATIBLE'] = 'IE=Edge, chrome=1'
        resp.headers['Cache-Control'] = 'public, max-age=0'
        await resp.prepare(request)
        await resp.write(image)
        return resp

    async def on_startup(self, app):
        """
        Функция, которая вызывается при старте приложения и инициализирует базу
        данных.
        """
        self.db = await Database.init(self.db)

    async def on_cleanup(self, app):
        """
        Функция, которая вызывается при закрытии приложения и корректно
        закрывает базу данных.
        """
        assert isinstance(self.db, Database)
        await self.db.close()

    def get_app(self):
        """
        Функция, которая запускает веб-приложение с необходимыми параметрами.
        """
        app = web.Application()
        app.router.add_get('/api/stat', self.get_stats)
        app.router.add_get('/api/picture', self.get_picture)
        app.on_startup.append(self.on_startup)
        app.on_cleanup.append(self.on_cleanup)
        return app
