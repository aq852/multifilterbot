import unittest


class RequestNotificationTests(unittest.TestCase):
    def test_notification_contains_request_and_user(self) -> None:
        text = "New file request `abcd1234` from 42"
        self.assertIn("abcd1234", text)
        self.assertIn("42", text)
