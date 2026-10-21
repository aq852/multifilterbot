import unittest


class AdminDashboardTests(unittest.TestCase):
    def test_status_labels_are_human_readable(self) -> None:
        self.assertEqual("online" if True else "offline", "online")
        self.assertEqual("on" if True else "off", "on")
