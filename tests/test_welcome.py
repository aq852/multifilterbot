import unittest


class WelcomeTests(unittest.TestCase):
    def test_multiple_names_are_joined(self) -> None:
        names = ["Amit", "Sara"]
        self.assertEqual(", ".join(names), "Amit, Sara")
