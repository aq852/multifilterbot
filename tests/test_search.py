import unittest

from app.services.search import build_search_terms, normalize_title, parse_media_filter, parse_search_filters, search_pattern
from app.handlers.search import _file_target


class SearchTests(unittest.TestCase):
    def test_normalize_title(self) -> None:
        self.assertEqual(normalize_title("Movie_2026.1080p [WEB-DL]"), "movie 2026 1080p web-dl")

    def test_terms_remove_short_tokens_and_duplicates(self) -> None:
        self.assertEqual(build_search_terms("The Movie Movie 4K"), ["4k", "movie"])

    def test_search_pattern_escapes_regex_characters(self) -> None:
        self.assertEqual(search_pattern("A+B"), r"a\ b")

    def test_parse_media_filter(self) -> None:
        self.assertEqual(parse_media_filter("video: My Movie"), ("My Movie", "video"))
        self.assertEqual(parse_media_filter("unknown:movie"), ("unknown:movie", None))

    def test_parse_metadata_filters(self) -> None:
        self.assertEqual(
            parse_search_filters("quality:WEB-DL resolution:1080p Hindi movie"),
            ("Hindi movie", {"quality": "web-dl", "resolution": "1080p"}),
        )

    def test_file_callback_target(self) -> None:
        self.assertEqual(_file_target("file:-100123:77"), (-100123, 77))
        self.assertIsNone(_file_target("file:not-a-chat:77"))
