import unittest


class FileInfoTests(unittest.TestCase):
    def test_info_callback_target_shape(self) -> None:
        parts = "fileinfo:-100123:77".split(":")
        self.assertEqual((int(parts[1]), int(parts[2])), (-100123, 77))
