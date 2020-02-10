from PIL import Image, ImageDraw
import io


def get_default_image():
    color = (0, 0, 0)
    img = Image.new('RGB', (1, 1), color)
    return img


def get_bytes_from_image(img):
    byte_io = io.BytesIO()
    img.save(byte_io, format='PNG')
    return bytes(byte_io.getvalue())


def create_image(data: dict):
    color = (0, 0, 120)
    img = Image.new('RGB', (80, 80), color)
    drawer = ImageDraw.Draw(img)
    drawer.text((0, 0), "ALL: ")
    day_label = f'DAY: {data["all"]["day"]}'
    drawer.text((10, 10), day_label)
    month_label = f'MONTH: {data["all"]["month"]}'
    drawer.text((10, 20), month_label)
    year_label = f'YEAR: {data["all"]["year"]}'
    drawer.text((10, 30), year_label)
    drawer.text((0, 40), 'UNIQUE: ')
    day_label = f'MONTH: {data["unique"]["month"]}'
    drawer.text((10, 50), day_label)
    month_label = f'YEAR: {data["unique"]["year"]}'
    drawer.text((10, 60), month_label)
    year_label = f'TOTAL: {data["unique"]["total"]}'
    drawer.text((10, 70), year_label)
    return img
