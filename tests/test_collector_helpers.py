import unittest
from datetime import datetime

from app.collector import canonical_url, _observation_identity, _identity_text


class CanonicalUrlTests(unittest.TestCase):
    def test_removes_tracking_parameters(self):
        self.assertEqual(canonical_url("https://Example.org/story?id=5&utm_source=rss&fbclid=abc#section"), "https://example.org/story?id=5")

    def test_preserves_meaningful_query(self):
        self.assertEqual(canonical_url("https://example.org/search?q=music&page=2"), "https://example.org/search?q=music&page=2")

    def test_empty_url(self):
        self.assertIsNone(canonical_url(None))


class ObservationIdentityTests(unittest.TestCase):
    def test_guid_and_url_changes_do_not_change_identity(self):
        first = {"external_id": "guid-A", "title": "L'Été — concert!", "published_at": datetime(2026, 5, 2, 10, 30), "url": "https://a.example/story"}
        second = {"external_id": "guid-B", "title": "L Ete concert", "published_at": datetime(2026, 5, 2, 10, 30), "url": "https://b.example/other"}
        self.assertEqual(_observation_identity(first), _observation_identity(second))

    def test_title_and_date_define_identity(self):
        base = {"title": "Actualité musicale", "published_raw": "02 May 2026"}
        self.assertNotEqual(_observation_identity(base), _observation_identity({"title": "Autre actualité", "published_raw": "02 May 2026"}))
        self.assertNotEqual(_observation_identity(base), _observation_identity({"title": "Actualité musicale", "published_raw": "03 May 2026"}))

    def test_normalizes_accents_punctuation_and_spaces(self):
        self.assertEqual(_identity_text("  L'Été — MUSIQUE! "), "l ete musique")

    def test_missing_title_or_date_is_rejected(self):
        with self.assertRaises(ValueError):
            _observation_identity({"title": "Sans date"})
        with self.assertRaises(ValueError):
            _observation_identity({"published_raw": "02 May 2026"})


if __name__ == "__main__":
    unittest.main()
