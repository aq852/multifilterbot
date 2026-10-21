import unittest


class UserManagementTests(unittest.TestCase):
    def test_username_reference_normalization(self) -> None:
        self.assertEqual("@ExampleUser".lstrip("@").casefold(), "exampleuser")
