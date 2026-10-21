import unittest

from app.config import settings


class DatabaseConfigTests(unittest.TestCase):
    def test_retry_settings_are_positive(self) -> None:
        self.assertGreater(settings.mongo_connect_retries, 0)
        self.assertGreater(settings.mongo_retry_delay, 0)
