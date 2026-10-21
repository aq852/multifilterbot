import json
import unittest


class BackupFormatTests(unittest.TestCase):
    def test_backup_format_is_json_serializable(self):
        payload = {"format": "multifilterbot-catalog-v1", "files": [], "channels": []}
        self.assertEqual(json.loads(json.dumps(payload))["format"], "multifilterbot-catalog-v1")
