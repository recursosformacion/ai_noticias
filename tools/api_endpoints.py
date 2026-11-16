"""Lista los endpoints publicos de la API de OSAP (solo lectura)."""
import json
import sys
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"


def main() -> int:
    spec = json.load(urllib.request.urlopen(f"{BASE}/openapi.json", timeout=10))
    print("API:", spec["info"].get("title"), spec["info"].get("version"))
    filtro = sys.argv[2].lower() if len(sys.argv) > 2 else None
    for path, ops in sorted(spec["paths"].items()):
        for method, op in ops.items():
            if method.lower() not in {"get", "post", "put", "delete", "patch"}:
                continue
            summary = (op.get("summary") or "")[:70]
            line = f"{method.upper():6} {path:58} {summary}"
            if filtro and filtro not in line.lower():
                continue
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
