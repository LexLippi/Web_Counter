from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from project.app import App
from PIL import Image
from project.imager import create_image, get_bytes_from_image


class TestApp(AioHTTPTestCase):
    async def get_application(self):
        return App().get_app()

    def test_init_app(self):
        app = App()
        self.assertIsInstance(app, App)
        self.assertIsInstance(app.db, str)
        self.assertIsInstance(app.IMAGE, bytes)

    @unittest_run_loop
    async def test_get_picture(self):
        resp = await self.client.request('GET', '/api/picture?id=1')
        color = (0, 0, 0)
        img = Image.new('RGB', (1, 1), color)
        img_bytes = get_bytes_from_image(img)
        resp_img_bytes = await resp.read()
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.content_type, 'image/png')
        self.assertEqual(resp_img_bytes, img_bytes)

    @unittest_run_loop
    async def test_get_stats(self):
        resp = await self.client.request('GET', '/api/stat?site=111&type=text')
        data = {"all": {"day": 0, "month": 0, "year": 0},
                "unique": {"month": 0, "year": 0, "total": 0}}
        self.assertEqual(resp.status, 200)
        self.assertEqual(str(data).replace("'", "\""), await resp.text())

    @unittest_run_loop
    async def test_get_image_with_stats(self):
        resp = await self.client.request('GET', '/api/stat?site=111&type=pic')
        data = {'all': {'day': 0, 'month': 0, 'year': 0},
                'unique': {'month': 0, 'year': 0, 'total': 0}}
        img_bytes = get_bytes_from_image(create_image(data))
        resp_img_bytes = await resp.read()
        self.assertEqual(resp.status, 200)
        self.assertEqual(resp.content_type, 'image/png')
        self.assertEqual(resp_img_bytes, img_bytes)

    @unittest_run_loop
    async def test_get_incorrect_stats(self):
        resp = await self.client.request('GET', '/api/stat?id=11')
        resp_exc = await resp.read()
        exp_exc = b'{\"status\": \"failed\", \"reason\": \"\'site\'\"}'
        self.assertEqual(resp.status, 500)
        self.assertEqual(resp_exc, exp_exc)

    @unittest_run_loop
    async def test_get_incorrect_query(self):
        resp = await self.client.request('GET', '/api/stast?id=11')
        self.assertEqual(resp.status, 404)
