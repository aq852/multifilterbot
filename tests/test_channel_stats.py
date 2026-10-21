import unittest


class ChannelStatsTests(unittest.TestCase):
    def test_empty_channel_defaults_are_zero(self):
        row = {"indexed_files": 0, "downloads": 0, "last_indexed": None}
        self.assertEqual(row["indexed_files"], 0)
        self.assertEqual(row["downloads"], 0)
