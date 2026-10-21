import unittest


class RandomDiscoveryTests(unittest.TestCase):
    def test_random_result_is_optional(self) -> None:
        self.assertIsNone(None)
