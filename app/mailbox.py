"""Buzón de entrada del módulo de noticias.

La recepción de correo **no se implementa aquí como servidor SMTP**: escuchar un
puerto y hablar SMTP en producción es trabajo de un MTA (Postfix, Exchange) o de
OSAP. Este módulo ofrece el punto de entrada para que esos sistemas depositen el
mensaje, con tres vías:

1. ``process_directory(path)``: procesa los ``.eml`` de una carpeta. Es la forma
   natural si un MDA (procmail, Maildrop, Exchange transport agent) deja cada
   mensaje en disco, y también sirve para pruebas e importaciones.

2. ``process_stdin()`` / ``process_file(path)``: para invocarlo desde un pipe.

3. ``process_message(raw)``: API directa para OSAP si prefiere reenviarlo por
   HTTP o mediante su bus de eventos.

Los mensajes fallidos se mueven a ``failed/`` con el motivo, para que un correo
mal formado no bloquee la cola.
"""
from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .news_service import NewsResponse, handle_raw_message
from .settings import ModuleSettings, load_settings

log = logging.getLogger(__name__)


@dataclass
class MailboxResult:
    processed: int = 0
    delivered: int = 0
    empty: int = 0
    rejected: int = 0
    duplicates: int = 0
    failed: int = 0
    responses: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "processed": self.processed,
            "delivery_queued": self.delivered,
            "empty": self.empty,
            "rejected": self.rejected,
            "duplicates": self.duplicates,
            "failed": self.failed,
            "errors": self.errors,
            "responses": self.responses,
        }


def _already_answered(connection, message_id: str | None) -> bool:
    """¿Este Message-ID ya tiene un mensaje de respuesta encolado?"""
    if not message_id:
        return False
    with connection.cursor() as cur:
        cur.execute(
            "SELECT id FROM email_requests WHERE message_id=%s",
            (message_id[:255],),
        )
        row = cur.fetchone()
        if not row:
            return False
        cur.execute(
            "SELECT COUNT(*) n FROM outbound_messages WHERE reference_id=%s",
            (str(row["id"]),),
        )
        return bool(cur.fetchone()["n"])


def _process_one(
    raw: bytes,
    connection,
    settings: ModuleSettings,
    delivery: str,
) -> NewsResponse:
    from .news_service import enqueue_response

    # Un reintento del MTA no debe producir un segundo correo al usuario.
    import email as _email

    message = _email.message_from_bytes(raw)
    message_id = (message.get("Message-ID") or "").strip() or None
    if _already_answered(connection, message_id):
        log.info("Mensaje %s ya respondido: se ignora", message_id)
        response = handle_raw_message(raw, connection, settings, persist=False)
        response.status = "DUPLICATE"
        return response

    response = handle_raw_message(raw, connection, settings, persist=True)
    if (
        delivery.upper() != "NONE"
        and response.message is not None
        and response.status not in {"REJECTED", "DUPLICATE"}
    ):
        token = enqueue_response(
            response, connection, delivery, settings.mail.outbound_dir
        )
        log.info("Respuesta %s entregada (%s)", response.request.sender, token)
    return response


def process_message(
    raw: bytes | str,
    connection,
    settings: ModuleSettings | None = None,
    delivery: str | None = None,
) -> NewsResponse:
    """Procesa un mensaje ya recibido y lo entrega al puerto de salida."""
    settings = settings or load_settings()
    return _process_one(raw, connection, settings, delivery or settings.mail.delivery)


def process_file(
    path: str | Path,
    connection,
    settings: ModuleSettings | None = None,
    delivery: str | None = None,
) -> NewsResponse:
    settings = settings or load_settings()
    return process_message(Path(path).read_bytes(), connection, settings, delivery)


def process_directory(
    directory: str | Path,
    connection,
    settings: ModuleSettings | None = None,
    delivery: str | None = None,
    failed_dir: str | Path | None = None,
) -> MailboxResult:
    """Procesa los ``.eml`` de una carpeta y los archiva al terminar."""
    settings = settings or load_settings()
    directory = Path(directory)
    failed_dir = Path(failed_dir) if failed_dir else directory / "failed"
    done_dir = directory / "processed"

    result = MailboxResult()
    if not directory.is_dir():
        result.errors.append(f"No existe la carpeta {directory}")
        return result

    for path in sorted(directory.glob("*.eml")):
        result.processed += 1
        try:
            response = process_message(path.read_bytes(), connection, settings, delivery)
            result.responses.append({
                "file": path.name,
                "status": response.status,
                "sender": response.request.sender,
                "topics": response.topics,
                "language": response.language,
                "items": len(response.hits),
            })
            if response.status == "DUPLICATE":
                result.duplicates += 1
            elif response.status == "REJECTED":
                result.rejected += 1
            elif response.status == "EMPTY":
                result.empty += 1
            else:
                result.delivered += 1
            done_dir.mkdir(exist_ok=True)
            shutil.move(str(path), str(done_dir / path.name))
        except Exception as exc:  # un correo roto no debe parar la cola
            result.failed += 1
            result.errors.append(f"{path.name}: {exc}")
            failed_dir.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(path), str(failed_dir / path.name))
            except OSError:
                pass
    return result


def process_stdin(
    connection,
    settings: ModuleSettings | None = None,
    delivery: str | None = None,
) -> NewsResponse:
    """Lee un mensaje desde la entrada estándar (útil para pipes del MDA)."""
    import sys

    raw = sys.stdin.buffer.read()
    return process_message(raw, connection, settings, delivery)
