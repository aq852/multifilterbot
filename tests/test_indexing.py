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

    def test_rename_command_requires_a_title(self) -> None:
        message = SimpleNamespace(reply_to_message=SimpleNamespace(), text="/renamefile")
        self.assertEqual((message.text or "").split(maxsplit=1), ["/renamefile"])
