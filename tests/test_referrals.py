import unittest

from app.services.referrals import parse_referrer


class ReferralTests(unittest.TestCase):
    def test_parse_valid_referrer(self) -> None:
        self.assertEqual(parse_referrer("ref_123", 456), 123)

    def test_reject_invalid_and_self_referral(self) -> None:
        self.assertIsNone(parse_referrer("ref_nope", 456))
        self.assertIsNone(parse_referrer("ref_456", 456))

