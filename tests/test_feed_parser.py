import unittest

from app.feed_parser import parse_feed


class FeedParserTests(unittest.TestCase):
    def test_rss(self):
        xml = b"""<?xml version="1.0"?><rss version="2.0"><channel>
        <title>Example</title><language>es</language><item>
        <title>Concierto &amp; estreno</title><link>https://example.org/a</link>
        <guid>item-1</guid><description><![CDATA[<p>Resumen</p>]]></description>
        <pubDate>Fri, 13 Nov 2026 10:00:00 GMT</pubDate>
        </item></channel></rss>"""
        meta, items = parse_feed(xml)
        self.assertEqual(meta["title"], "Example")
        self.assertEqual(items[0]["title"], "Concierto & estreno")
        self.assertEqual(items[0]["external_id"], "item-1")
        self.assertEqual(items[0]["language"], "es")
        self.assertEqual(items[0]["published_at"].isoformat(), "2026-11-13T10:00:00")

    def test_atom(self):
        xml = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
        <title>Feed</title><entry><title>News</title><id>tag:example.org,2026:1</id>
        <link href="https://example.org/news/1"/><summary>Summary</summary>
        <updated>2026-11-13T10:00:00Z</updated></entry></feed>"""
        _, items = parse_feed(xml)
        self.assertEqual(items[0]["url"], "https://example.org/news/1")
        self.assertEqual(items[0]["updated_at"].isoformat(), "2026-11-13T10:00:00")

    def test_rejects_html(self):
        with self.assertRaises(ValueError):
            parse_feed(b"<html><body>not a feed</body></html>")


if __name__ == "__main__":
    unittest.main()
