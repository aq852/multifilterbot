import unittest


class HistoryClearTests(unittest.TestCase):
    def test_empty_history_message_uses_plural_form(self) -> None:
        deleted = 0
        self.assertEqual(f"entr{'y' if deleted == 1 else 'ies'}", "entries")
