"""Configuración local de ai_noticias."""
from __future__ import annotations

import os
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_config() -> dict:
    path = ROOT / "osap.toml"
    if not path.is_file():
        raise RuntimeError(
            f"No existe {path}. Copia osap.example.toml a osap.toml y configura el entorno local."
        )
    with path.open("rb") as handle:
        raw = tomllib.load(handle)
    db = raw.get("db")
    if not isinstance(db, dict):
        raise RuntimeError("Falta la sección [db] en osap.toml.")
    name = str(db.get("name") or "")
    if name != "osap_noticias":
        raise RuntimeError(
            f"El nombre configurado es {name!r}; se esperaba 'osap_noticias'. "
            "Se cancela para proteger otras bases."
        )
    if not db.get("user"):
        raise RuntimeError("Falta db.user en osap.toml.")
    return {
        "host": db.get("host", "127.0.0.1"),
        "port": int(db.get("port", 3306)),
        "user": db["user"],
        "password": os.environ.get("OSAP_DB_PASSWORD", db.get("password", "")),
        "database": name,
        "charset": "utf8mb4",
        "autocommit": False,
        "connect_timeout": 10,
        "read_timeout": 30,
        "write_timeout": 30,
    }
