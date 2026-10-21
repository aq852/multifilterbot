import unittest

from app.handlers.settings import _keyboard


class SettingsTests(unittest.TestCase):
    def test_keyboard_toggles_current_state(self) -> None:
        keyboard = _keyboard(False, True)
        self.assertEqual(keyboard.inline_keyboard[0][0].callback_data, "settings:maintenance:on")
        self.assertEqual(keyboard.inline_keyboard[1][0].callback_data, "settings:approve:off")

