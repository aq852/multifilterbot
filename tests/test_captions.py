import unittest

from app.services.captions import format_size, render_caption


class CaptionTests(unittest.TestCase):
    def test_render_caption_placeholders(self) -> None:
        result = render_caption("{title} | {type} | {size}", {
            "title": "Example Movie", "media_type": "video", "size": 1024 * 1024,
        })
        self.assertEqual(result, "Example Movie | video | 1.0 MB")

    def test_invalid_placeholder_falls_back_to_title(self) -> None:
        self.assertEqual(render_caption("{unknown}", {"title": "Fallback"}), "Fallback")

    def test_format_size_without_size(self) -> None:
        self.assertEqual(format_size(None), "unknown size")

