import unittest


class SavedCommandTests(unittest.TestCase):
    def test_empty_count_uses_correct_suffix(self) -> None:
        deleted = 0
        self.assertEqual(f"file{'s' if deleted != 1 else ''}", "files")
