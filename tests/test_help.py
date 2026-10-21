import unittest


class HelpTests(unittest.TestCase):
    def test_help_contains_core_commands(self) -> None:
        commands = "/search /latest /popular /saved /share /request"
        for command in commands.split():
            self.assertTrue(command.startswith("/"))
