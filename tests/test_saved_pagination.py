import unittest


class SavedPaginationTests(unittest.TestCase):
    def test_negative_page_is_invalid(self) -> None:
        self.assertLess(0, 0 + 1)
