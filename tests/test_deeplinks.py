import unittest

from app.services.deeplinks import build_file_payload, parse_file_payload


class DeepLinkTests(unittest.TestCase):
    def test_file_payload_round_trip(self) -> None:
        payload = build_file_payload(-100123, 77)
        self.assertEqual(parse_file_payload(payload), (-100123, 77))

    def test_invalid_payload_is_rejected(self) -> None:
        self.assertIsNone(parse_file_payload("file_bad_77"))
        self.assertIsNone(parse_file_payload("ref_12"))
