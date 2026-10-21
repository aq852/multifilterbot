import unittest

from app.services.commands import ADMIN_COMMANDS, USER_COMMANDS


class CommandMenuTests(unittest.TestCase):
    def test_admin_menu_contains_user_and_admin_commands(self):
        user_names = {command.command for command in USER_COMMANDS}
        admin_names = {command.command for command in ADMIN_COMMANDS}
        self.assertTrue(user_names <= admin_names)
        self.assertIn("audit", admin_names)

    def test_user_menu_contains_diagnostics(self):
        self.assertIn("ping", {command.command for command in USER_COMMANDS})
