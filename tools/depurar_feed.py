"""Muestra las etiquetas de los elementos de un feed para depurar el parser.

Uso: py -3 -m tools.depurar_feed <url>
"""
from __future__ import annotations

import ssl
import sys
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

import certifi

from app.collector import USER_AGENT
from app.feed_parser import _local

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def main() -> int:
    url = sys.argv[1]
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=25, context=SSL_CONTEXT) as response:
        body = response.read()
    root = ET.fromstring(body)
    entries = [n for n in root.iter() if _local(n.tag) in {"item", "entry"}]
    print(f"elementos: {len(entries)}")
    first = entries[0]
    print("hijos del primer elemento:")
    for child in list(first):
        text = "".join(child.itertext()).strip()
        print(f"  <{child.tag}> len={len(text)} -> {text[:120]!r}")
    print("contenido crudo del primer elemento (primeros 1200 bytes):")
    print(ET.tostring(first, encoding="unicode")[:1200])
    return 0


if __name__ == "__main__":
    sys.exit(main())
