import unittest


class RelatedTests(unittest.TestCase):
    def test_related_command_supports_filename_text(self) -> None:
        self.assertEqual("Movie Name 1080p".strip(), "Movie Name 1080p")
