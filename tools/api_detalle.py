"""Detalle de un endpoint de la API de OSAP (parametros y esquema de respuesta)."""
import json
import sys
import urllib.request

BASE = sys.argv[1]
PATH = sys.argv[2]
METHOD = (sys.argv[3] if len(sys.argv) > 3 else "get").lower()


def resolve(spec, schema, depth=0):
    if depth > 3 or not isinstance(schema, dict):
        return schema
    if "$ref" in schema:
        name = schema["$ref"].rsplit("/", 1)[-1]
        return resolve(spec, spec["components"]["schemas"].get(name, {}), depth + 1)
    if schema.get("type") == "array":
        return [resolve(spec, schema.get("items", {}), depth + 1)]
    if "properties" in schema:
        return {k: resolve(spec, v, depth + 1) for k, v in schema["properties"].items()}
    return schema.get("type", schema)


def main() -> int:
    spec = json.load(urllib.request.urlopen(f"{BASE}/openapi.json", timeout=10))
    op = spec["paths"].get(PATH, {}).get(METHOD)
    if not op:
        print("No existe ese endpoint")
        return 1
    print("SUMMARY:", op.get("summary"))
    print("SECURITY:", op.get("security"))
    print("PARAMS:")
    for p in op.get("parameters", []):
        print("  ", p.get("in"), p.get("name"), p.get("required"), p.get("schema"))
    rb = op.get("requestBody")
    if rb:
        print("BODY:", json.dumps(resolve(spec, rb), ensure_ascii=False)[:600])
    print("RESPONSE:")
    print(json.dumps(resolve(spec, op.get("responses", {}).get("200", {})),
                     ensure_ascii=False)[:1500])
    return 0


if __name__ == "__main__":
    sys.exit(main())
