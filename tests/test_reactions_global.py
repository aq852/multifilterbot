import unittest

from app.handlers.automation import _parse_emojis


class GlobalReactionTests(unittest.TestCase):
    def test_global_emoji_list_is_bounded_by_command_contract(self) -> None:
        self.assertLessEqual(len(_parse_emojis("🔥,❤️,👍,😂,🎉")), 5)
