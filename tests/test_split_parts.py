import unittest

from app.services.split_parts import split_part_info


class SplitPartTests(unittest.TestCase):
    def test_numeric_parts(self):
        self.assertEqual(split_part_info("movie.mkv.001"), ("movie.mkv", 1))

    def test_named_parts(self):
        self.assertEqual(split_part_info("archive.part2"), ("archive", 2))

    def test_regular_name_is_not_a_part(self):
        self.assertIsNone(split_part_info("movie.mkv"))
