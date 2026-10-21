import unittest

from aiogram.types import Message

from app.middlewares.audit import _action_name


class AuditTests(unittest.TestCase):
    def test_action_name_keeps_only_command(self):
        self.assertEqual(_action_name(Message(message_id=1, date=0, chat={"id": 1, "type": "private"}, text="/ban 123")), "/ban")

    def test_non_command_is_ignored(self):
        self.assertIsNone(_action_name(Message(message_id=1, date=0, chat={"id": 1, "type": "private"}, text="hello")))
