import unittest

from app.handlers.automation import _parse_emojis


class ReactionTests(unittest.TestCase):
    def test_parse_multiple_emojis(self) -> None:
        self.assertEqual(_parse_emojis("🔥, ❤️, 👍"), ["🔥", "❤️", "👍"])
