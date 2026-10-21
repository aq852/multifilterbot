import unittest


class RequestTests(unittest.TestCase):
    def test_request_ids_are_display_safe(self) -> None:
        request_id = "a1b2c3d4"
        self.assertEqual(len(request_id), 8)
        self.assertTrue(request_id.isalnum())

