import unittest

from app.config import Settings


class ConfigTests(unittest.TestCase):
    def test_admin_ids_accept_comma_separated_values(self) -> None:
        config = Settings(bot_token="token", admin_ids="123, 456")
        self.assertEqual(config.admin_ids, [123, 456])


if __name__ == "__main__":
    unittest.main()
