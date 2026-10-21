import unittest

from app.services.telegram_links import parse_message_link


class TelegramLinkTests(unittest.TestCase):
    def test_public_message_link(self):
        self.assertEqual(parse_message_link("https://t.me/example_channel/42"), ("example_channel", 42))

    def test_private_message_link(self):
        self.assertEqual(parse_message_link("https://t.me/c/123456/42"), ("123456", 42))

    def test_invalid_link(self):
        self.assertIsNone(parse_message_link("https://example.com/file/42"))
