import unittest

from app.services.premium import get_plan, payment_payload, plan_from_payload


class PremiumTests(unittest.TestCase):
    def test_payload_round_trip(self) -> None:
        self.assertEqual(plan_from_payload(payment_payload("monthly")), get_plan("monthly"))

    def test_invalid_payload_is_rejected(self) -> None:
        self.assertIsNone(plan_from_payload("premium:unknown"))
        self.assertIsNone(plan_from_payload("other:monthly"))

