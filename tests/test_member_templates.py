import unittest


class MemberTemplateTests(unittest.TestCase):
    def test_name_placeholder_is_replaced(self) -> None:
        self.assertEqual("Welcome, {name}!".replace("{name}", "Amit"), "Welcome, Amit!")
