import unittest

from app.services.deeplinks import build_link_payload, parse_link_payload


class ShareLinkTests(unittest.TestCase):
    def test_link_payload_round_trip(self):
        token = "0123456789abcdef"
        self.assertEqual(parse_link_payload(build_link_payload(token)), token)

    def test_invalid_link_payload_is_rejected(self):
        self.assertIsNone(parse_link_payload("link_short"))
