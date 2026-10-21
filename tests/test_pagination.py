import unittest

from app.handlers.search import _page_target


class PaginationTests(unittest.TestCase):
    def test_page_callback_target(self) -> None:
        self.assertEqual(_page_target("search:abc123:2"), ("abc123", 2))

    def test_invalid_page_callback_is_rejected(self) -> None:
        self.assertIsNone(_page_target("search:abc123:-1"))
        self.assertIsNone(_page_target("file:1:2"))

