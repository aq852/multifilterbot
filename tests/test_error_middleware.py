import unittest

from app.middlewares.errors import ErrorMiddleware


class ErrorMiddlewareTests(unittest.TestCase):
    def test_middleware_can_be_constructed(self) -> None:
        self.assertIsInstance(ErrorMiddleware(), ErrorMiddleware)
