import unittest

from app.collector import canonical_url


class CanonicalUrlTests(unittest.TestCase):
    def test_removes_tracking_parameters(self):
        self.assertEqual(
            canonical_url("https://Example.org/story?id=5&utm_source=rss&fbclid=abc#section"),
            "https://example.org/story?id=5",
        )

    def test_preserves_meaningful_query(self):
        self.assertEqual(
            canonical_url("https://example.org/search?q=music&page=2"),
            "https://example.org/search?q=music&page=2",
        )

    def test_empty_url(self):
        self.assertIsNone(canonical_url(None))


if __name__ == "__main__":
    unittest.main()
