from project.app import App
import argparse
from aiohttp import web


def parse_args():
    """
    Функия, обрабатывающая аргументы запуска и возвращающая их в необходимом
    формате
    """
    arg_parser = argparse.ArgumentParser(
        description='aiohttp.web Application server', prog='aiohttp.web')
    arg_parser.add_argument(
        '-ho', '--hostname',
        help='TCP/IP hostname to serve on (default: localhost)',
        default='0.0.0.0')
    arg_parser.add_argument(
        '-p', '--port',
        help='TCP/IP port to serve on (default: 8080)',
        type=int,
        default='8080')
    arg_parser.add_argument(
        '-f', '--filename',
        help='database filename',
        default='count_visitors.db')
    return arg_parser.parse_args()


if __name__ == '__main__':
    """
    Основной метод, где запускается сервер с параметрами адрес хоста,
    адрес порта, имя файла с базой данных, и начинает подсчитываться
    статистика посещений.
    """
    args = parse_args()
    app = App(db=args.filename).get_app()
    web.run_app(app, host=args.hostname, port=args.port)
