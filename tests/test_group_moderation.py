import unittest

from app.handlers.automation import _has_link


class GroupModerationTests(unittest.TestCase):
    def test_link_detection(self) -> None:
        self.assertTrue(_has_link("Join https://example.com"))
        self.assertFalse(_has_link("No external link here"))
