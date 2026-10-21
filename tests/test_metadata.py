import unittest

from app.services.metadata import extract_metadata


class MetadataTests(unittest.TestCase):
    def test_extract_media_metadata(self) -> None:
        result = extract_metadata("Example S02E03 1080p WEB-DL Hindi")
        self.assertEqual(result["season"], "S02")
        self.assertEqual(result["resolution"], "1080p")
        self.assertEqual(result["quality"], "WEB-DL")
        self.assertEqual(result["language"], "Hindi")

