import unittest

from app.collector import canonical_url, _observation_identity


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


class ObservationIdentityTests(unittest.TestCase):
    def test_guid_is_preferred(self):
        item = {"external_id": "guid-123", "title": "A", "published_raw": "today", "url": "https://example.org"}
        self.assertEqual(_observation_identity(item), "guid-123")

    def test_shared_url_does_not_define_identity(self):
        first = {"external_id": None, "title": "Entry A", "published_raw": "01 Jan 2024", "url": "https://example.org/search"}
        second = {"external_id": None, "title": "Entry B", "published_raw": "02 Jan 2024", "url": "https://example.org/search"}
        self.assertNotEqual(_observation_identity(first), _observation_identity(second))

    def test_fallback_identity_is_stable(self):
        first = {"external_id": None, "title": "  Entry   A ", "published_raw": "01 Jan 2024"}
        second = {"external_id": None, "title": "entry a", "published_raw": "01 Jan 2024"}
        self.assertEqual(_observation_identity(first), _observation_identity(second))


if __name__ == "__main__":
    unittest.main()
