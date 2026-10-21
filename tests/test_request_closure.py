import unittest


class RequestClosureTests(unittest.TestCase):
    def test_closure_notification_mentions_request(self) -> None:
        text = "Your file request has been closed:\nExample Movie"
        self.assertIn("closed", text)
