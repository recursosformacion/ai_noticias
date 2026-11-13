import unittest
from unittest.mock import patch

from app.collector import probe_candidate_channels


class FakeCursor:
    def __init__(self, rows):
        self.rows = rows
        self.sql = ""

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, sql, params=()):
        self.sql = sql
        self.params = params

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, rows):
        self.cursor_instance = FakeCursor(rows)

    def cursor(self):
        return self.cursor_instance


class ProbeTests(unittest.TestCase):
    def test_probe_reports_metadata_without_persisting_feed_content(self):
        channel = {
            "id": 1,
            "publisher_id": 1,
            "provider_name": "RSS",
            "name": "In the Muse",
            "url": "https://blogs.loc.gov/music/feed/",
            "domain": "loc.gov",
        }
        xml = b"""<rss version="2.0"><channel><title>Example feed</title>
        <item><title>Private test title</title><link>/story/1</link>
        <guid>entry-1</guid><author>Staff author</author>
        <pubDate>Fri, 13 Nov 2026 10:00:00 GMT</pubDate></item>
        </channel></rss>"""
        connection = FakeConnection([channel])
        with patch("app.collector._fetch", return_value=(
            200, xml, {"ETag": '"abc"'}, "https://blogs.loc.gov/music/feed/"
        )) as fetch:
            result = probe_candidate_channels(connection)

        fetch.assert_called_once()
        self.assertIn("SELECT", connection.cursor_instance.sql.upper())
        self.assertNotIn("INSERT", connection.cursor_instance.sql.upper())
        self.assertEqual(result[0]["status"], "OK")
        self.assertEqual(result[0]["items"], 1)
        self.assertEqual(result[0]["items_with_author"], 1)
        self.assertFalse(result[0]["persisted"])
        self.assertNotIn("Private test title", str(result))

    def test_probe_rejects_redirect_outside_allowed_domain(self):
        channel = {
            "id": 1, "publisher_id": 1, "provider_name": "RSS",
            "name": "In the Muse", "url": "https://blogs.loc.gov/music/feed/",
            "domain": "loc.gov",
        }
        connection = FakeConnection([channel])
        with patch("app.collector._fetch", return_value=(
            200, b"<rss><channel><title>x</title></channel></rss>", {},
            "https://example.com/feed"
        )):
            result = probe_candidate_channels(connection)
        self.assertEqual(result[0]["status"], "ERROR")
        self.assertIn("dominio autorizado", result[0]["reason"])


if __name__ == "__main__":
    unittest.main()
