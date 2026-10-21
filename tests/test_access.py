import unittest

from app.services.referrals import parse_referrer


class AccessTests(unittest.TestCase):
    def test_referral_parser_remains_safe_for_malformed_access_input(self) -> None:
        self.assertIsNone(parse_referrer("ref_", 1))

