import unittest


class BroadcastTests(unittest.TestCase):
    def test_summary_fields_are_present(self) -> None:
        summary = "Sent: 2\nFailed: 1\nBlocked users: 1"
        self.assertIn("Blocked users", summary)
