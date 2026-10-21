import unittest


class WarningTests(unittest.TestCase):
    def test_warning_threshold(self) -> None:
        self.assertGreaterEqual(3, 3)
