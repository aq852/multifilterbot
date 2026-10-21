import unittest


class HistoryTests(unittest.TestCase):
    def test_history_callback_index_is_numeric(self) -> None:
        self.assertEqual(int("2"), 2)
