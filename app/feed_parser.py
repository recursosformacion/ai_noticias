"""Parser RSS 2.0 y Atom basado en la biblioteca estándar."""
from __future__ import annotations

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from xml.etree import ElementTree as ET
from urllib.parse import urljoin


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def _child_text(element, names: set[str]) -> str | None:
    for child in list(element):
        if _local(child.tag) in names:
            value = "".join(child.itertext()).strip()
            if value:
                return value
    return None


def _atom_link(element) -> str | None:
    links = [child for child in list(element) if _local(child.tag) == "link"]
    for link in links:
        rel = link.attrib.get("rel", "alternate")
        href = link.attrib.get("href")
        if href and rel in ("alternate", ""):
            return href.strip()
    return links[0].attrib.get("href") if links else None


def _date(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip()
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(tzinfo=None)


def parse_feed(xml_bytes: bytes, base_url: str | None = None) -> tuple[dict, list[dict]]:
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ValueError(f"El documento no es XML RSS/Atom válido: {exc}") from exc

    root_name = _local(root.tag)
    if root_name == "feed":
        channel = root
        entries = [node for node in list(root) if _local(node.tag) == "entry"]
        title = _child_text(channel, {"title"})
        language = channel.attrib.get("{http://www.w3.org/XML/1998/namespace}lang")
    else:
        channel = root
        if root_name == "rss":
            channel = next((n for n in list(root) if _local(n.tag) == "channel"), root)
        elif root_name == "rdf":
            entries = [node for node in list(root) if _local(node.tag) == "item"]
            title = _child_text(root, {"title"})
            language = None
            return _normalize(entries, title, language, base_url)
        if _local(channel.tag) not in {"channel", "rdf"}:
            raise ValueError("El XML recibido no parece un feed RSS 2.0 ni Atom.")
        entries = [node for node in list(channel) if _local(node.tag) == "item"]
        title = _child_text(channel, {"title"})
        language = _child_text(channel, {"language"})

    if root_name not in {"rss", "feed", "rdf"}:
        raise ValueError("Formato de feed no soportado.")
    return _normalize(entries, title, language, base_url)


def _normalize(entries, feed_title, feed_language, base_url=None):
    items = []
    for entry in entries:
        atom = _local(entry.tag) == "entry"
        title = _child_text(entry, {"title"})
        if not title:
            continue
        link = _atom_link(entry) if atom else _child_text(entry, {"link"})
        if link and base_url:
            link = urljoin(base_url, link.strip())
        guid = _child_text(entry, {"id"}) if atom else _child_text(entry, {"guid"})
        description = _child_text(entry, {"summary", "description", "encoded"})
        author = _child_text(entry, {"author", "creator"})
        if author and author.strip().startswith("<"):
            author = _child_text(next((n for n in list(entry) if _local(n.tag) == "author"), entry), {"name"}) or author
        published_raw = _child_text(entry, {"published", "pubdate", "date", "created"})
        updated_raw = _child_text(entry, {"updated", "modified"})
        language = entry.attrib.get("{http://www.w3.org/XML/1998/namespace}lang") or feed_language
        items.append({
            "title": unescape(title).strip(),
            "url": unescape(link).strip() if link else None,
            "external_id": unescape(guid).strip() if guid else None,
            "description": unescape(description).strip() if description else None,
            "author": unescape(author).strip() if author else None,
            "published_raw": published_raw,
            "published_at": _date(published_raw),
            "updated_raw": updated_raw,
            "updated_at": _date(updated_raw),
            "language": language,
        })
    return {"title": feed_title, "language": feed_language}, items
