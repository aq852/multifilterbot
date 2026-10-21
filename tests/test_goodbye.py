import unittest


class GoodbyeTests(unittest.TestCase):
    def test_goodbye_message_contains_member_name(self) -> None:
        name = "Amit"
        self.assertIn(name, f"Goodbye, {name}! Take care.")
