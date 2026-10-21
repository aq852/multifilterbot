import unittest

from app.health import started_at


class HealthTests(unittest.TestCase):
    def test_health_start_time_exists(self):
        self.assertGreaterEqual(started_at, 0)
