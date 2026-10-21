import unittest

from app.handlers.saved import _target


class SavedFileTests(unittest.TestCase):
    def test_target_parser(self) -> None:
        self.assertEqual(_target("save:-100123:77", "save"), (-100123, 77))
        self.assertIsNone(_target("save:bad:77", "save"))
        self.assertIsNone(_target("unsave:1:2", "save"))
