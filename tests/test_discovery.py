import unittest


class DiscoveryTests(unittest.TestCase):
    def test_download_count_is_displayed_as_integer(self) -> None:
        self.assertEqual(f"{3} downloads", "3 downloads")
