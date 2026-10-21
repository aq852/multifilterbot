import unittest


class ReactionIgnoreTests(unittest.TestCase):
    def test_chat_id_is_integer(self) -> None:
        self.assertEqual(int("-100123"), -100123)
