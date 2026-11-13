"""Helpers for accessing the local MariaDB configured in osap.toml."""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
import tomllib


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "osap.toml"


def load_db_config() -> dict:
    if not CONFIG_PATH.is_file():
        raise RuntimeError(
            f"No se encuentra {CONFIG_PATH}. Restaura tu osap.toml local; "
            "el fichero está excluido de Git."
        )

    with CONFIG_PATH.open("rb") as handle:
        config = tomllib.load(handle)

    db = config.get("db")
    if not isinstance(db, dict):
        raise RuntimeError("osap.toml debe contener una sección [db].")

    result = {
        "host": str(db.get("host") or "127.0.0.1"),
        "port": int(db.get("port") or 3306),
        "name": str(db.get("name") or ""),
        "user": str(db.get("user") or ""),
        "password": os.environ.get("OSAP_DB_PASSWORD", db.get("password", "")),
    }

    if result["name"] != "osap_noticias":
        raise RuntimeError(
            "La configuración no apunta a osap_noticias. "
            "Se cancela para evitar modificar otra base de datos."
        )
    if not result["user"]:
        raise RuntimeError("Falta db.user en osap.toml.")
    return result


class MysqlClient:
    def __init__(self, config: dict):
        self.config = config
        self.executable = shutil.which("mysql")
        if not self.executable:
            raise RuntimeError(
                "No se encuentra mysql.exe en PATH. Añade la carpeta bin de MariaDB."
            )
        self.option_file = None
        self.option_path = None

    def __enter__(self):
        values = {
            "host": self.config["host"],
            "port": str(self.config["port"]),
            "user": self.config["user"],
            "database": self.config["name"],
            "default-character-set": "utf8mb4",
        }
        if self.config["password"]:
            values["password"] = self.config["password"]

        def quote(value: str) -> str:
            return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r") + '"'

        content = "[client]\n" + "".join(
            f"{key}={quote(value)}\n" for key, value in values.items()
        )
        handle = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".cnf", prefix="ai_noticias_",
            delete=False, newline="\n"
        )
        try:
            handle.write(content)
        finally:
            handle.close()
        self.option_path = Path(handle.name)
        try:
            os.chmod(self.option_path, 0o600)
        except OSError:
            pass
        return self

    def run(self, sql: str, *, stdin: bool = False) -> str:
        import subprocess

        command = [
            self.executable,
            f"--defaults-extra-file={self.option_path}",
            "--batch",
            "--raw",
        ]
        if stdin:
            completed = subprocess.run(
                command, input=sql, text=True, capture_output=True,
                cwd=ROOT, encoding="utf-8", errors="replace"
            )
        else:
            completed = subprocess.run(
                command + ["--skip-column-names", "--execute", sql],
                text=True, capture_output=True, cwd=ROOT,
                encoding="utf-8", errors="replace"
            )
        if completed.returncode:
            # The client output may contain SQL/server diagnostics, never credentials.
            detail = (completed.stderr or completed.stdout).strip()
            raise RuntimeError(detail or f"mysql terminó con código {completed.returncode}.")
        return completed.stdout.strip()

    def __exit__(self, exc_type, exc, tb):
        if self.option_path:
            try:
                self.option_path.unlink(missing_ok=True)
            except OSError:
                pass
