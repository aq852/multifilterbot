import unittest

from app.services.search import build_search_terms, normalize_title, search_pattern


class SearchTests(unittest.TestCase):
    def test_normalize_title(self) -> None:
        self.assertEqual(normalize_title("Movie_2026.1080p [WEB-DL]"), "movie 2026 1080p web-dl")

    def test_terms_remove_short_tokens_and_duplicates(self) -> None:
        self.assertEqual(build_search_terms("The Movie Movie 4K"), ["4k", "movie"])

    def test_search_pattern_escapes_regex_characters(self) -> None:
        self.assertEqual(search_pattern("A+B"), r"a\ b")
