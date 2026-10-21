import unittest
from unittest.mock import patch

from app.middlewares.rate_limit import RateLimitMiddleware


class RateLimitTests(unittest.TestCase):
    @patch("app.middlewares.rate_limit.settings.rate_limit_window", 10.0)
    @patch("app.middlewares.rate_limit.settings.rate_limit_burst", 2)
    def test_burst_is_limited(self) -> None:
        limiter = RateLimitMiddleware()
        self.assertTrue(limiter._allowed(1))
        self.assertTrue(limiter._allowed(1))
        self.assertFalse(limiter._allowed(1))
