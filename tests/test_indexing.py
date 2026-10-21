import unittest
from types import SimpleNamespace

from app.handlers.indexing import _file_target


class IndexingTests(unittest.TestCase):
    def test_file_target_from_command(self) -> None:
        message = SimpleNamespace(reply_to_message=None, text="/deletefile -100123 77")
        self.assertEqual(_file_target(message), (-100123, 77))

    def test_invalid_file_target(self) -> None:
        message = SimpleNamespace(reply_to_message=None, text="/deletefile nope")
        self.assertIsNone(_file_target(message))
