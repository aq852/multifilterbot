import unittest


class ShareCallbackTests(unittest.TestCase):
    def test_share_callback_target_shape(self) -> None:
        parts = "share:-100123:77".split(":")
        self.assertEqual((int(parts[1]), int(parts[2])), (-100123, 77))
