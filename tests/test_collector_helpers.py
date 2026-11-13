import unittest

from app.collector import (
    canonical_url,
    _observation_identity,
    _identity_text,
    _normalized_description,
)


class CanonicalUrlTests(unittest.TestCase):
    def test_removes_tracking_parameters(self):
        self.assertEqual(canonical_url("https://Example.org/story?id=5&utm_source=rss&fbclid=abc#section"), "https://example.org/story?id=5")

    def test_preserves_meaningful_query(self):
        self.assertEqual(canonical_url("https://example.org/search?q=music&page=2"), "https://example.org/search?q=music&page=2")

    def test_empty_url(self):
        self.assertIsNone(canonical_url(None))


class ObservationIdentityTests(unittest.TestCase):
    def test_description_alone_defines_identity(self):
        first = {
            "title": "Primera noticia",
            "description": "La Orquesta anuncia una nueva temporada de conciertos.",
            "published_raw": "02 May 2026",
            "url": "https://a.example/story",
            "external_id": "guid-A",
        }
        second = {
            "title": "Otro titular",
            "description": "La Orquesta anuncia una nueva temporada de conciertos.",
            "published_raw": "03 May 2026",
            "url": "https://b.example/other",
            "external_id": "guid-B",
        }
        self.assertEqual(_observation_identity(first), _observation_identity(second))

    def test_normalizes_html_entities_accents_punctuation_and_spaces(self):
        first = "  <p>L'Été — MUSIQUE!</p> &amp; concerts "
        second = "L Ete musique et concerts"
        self.assertEqual(_normalized_description(first), _normalized_description(second))
        self.assertEqual(_observation_identity({"description": first}), _observation_identity({"description": second}))

    def test_removes_script_and_style_content(self):
        self.assertEqual(_normalized_description("Texto <script>alert('x')</script> final"), "texto final")

    def test_missing_or_empty_description_is_rejected(self):
        with self.assertRaises(ValueError):
            _observation_identity({"title": "Sin descripción"})
        with self.assertRaises(ValueError):
            _observation_identity({"description": "<p> &nbsp; </p>"})


if __name__ == "__main__":
    unittest.main()
