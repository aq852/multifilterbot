import unittest
from types import SimpleNamespace

from app.handlers.management import _target_user_id


class ManagementTargetTests(unittest.IsolatedAsyncioTestCase):
    async def test_target_can_come_from_reply(self) -> None:
        message = SimpleNamespace(
            reply_to_message=SimpleNamespace(from_user=SimpleNamespace(id=42)),
            text="/warn",
        )
        self.assertEqual(await _target_user_id(message), 42)
