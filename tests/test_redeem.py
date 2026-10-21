import unittest

from app.services.redeem import normalize_code, redeem_charge_id


class RedeemTests(unittest.TestCase):
    def test_normalize_code(self) -> None:
        self.assertEqual(normalize_code(" spring-2026! "), "SPRING-2026")

    def test_charge_id_is_user_specific(self) -> None:
        self.assertEqual(redeem_charge_id("gift", 42), "redeem:GIFT:42")

