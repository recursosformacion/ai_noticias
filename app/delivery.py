"""Puerto de entrega del correo (ADR-006 de OSAP).

Decisión de arquitectura: **ai_noticias no envía correo**. Su responsabilidad es
responder a una consulta con la lista de noticias y dejar el mensaje construido en
una cola de salida. El envío corresponde a OSAP, que ya es el propietario de las
comunicaciones (`osap-support`, ``EmailSender`` / ``CommunicationEvent``).

Este módulo define el contrato y las implementaciones de entrega:

- ``QueueDelivery``: deja el mensaje en ``outbound_messages`` (por defecto). Permite
  que OSAP lo recoja y envíe con el proveedor que corresponda, sin compartir
  credenciales SMTP ni duplicar plantillas.
- ``FileDelivery``: escribe el ``.eml`` en disco. Útil en desarrollo y en pruebas.

Añadir un envío SMTP directo aquí volvería a partir la propiedad del correo en dos
servicios, así que no se implementa.
"""
from __future__ import annotations

import logging
from copy import deepcopy
from dataclasses import dataclass
from email.message import Message
from pathlib import Path
from typing import Protocol

log = logging.getLogger(__name__)


@dataclass
class OutboundMessage:
    """Mensaje listo para entregar.

    Se conservan los cuerpos ya renderizados porque ``ai_noticias`` es quien conoce
    el idioma y las plantillas; OSAP solo transporta.
    """

    subject: str
    body_text: str
    body_html: str
    message: Message
    # Destinatario: cuenta de OSAP (preferente) o dirección explícita (pruebas).
    user_ref: str | None = None
    recipient_address: str | None = None
    kind: str = "NEWS_DIGEST"
    origin: str = "AI_NOTICIAS"
    reference: str | None = None  # id de la consulta que lo origina
    language: str = "es"
    items: int = 0
    digest_date: str | None = None
    digest_window_days: int | None = None

    def __post_init__(self) -> None:
        if not self.user_ref and not self.recipient_address:
            raise ValueError(
                "El mensaje necesita user_ref (cuenta OSAP) o recipient_address."
            )

    @property
    def label(self) -> str:
        return self.user_ref or self.recipient_address or "?"

    def email_message_copy(self) -> Message:
        """Copia del mensaje con un ``To:`` legible para el fichero .eml."""
        clone = deepcopy(self.message)
        if self.recipient_address:
            del clone["To"]
            clone["To"] = self.recipient_address
        elif clone["To"]:
            # Sin dirección no hay buzón que mostrar; se deja el identificador.
            del clone["To"]
            clone["To"] = f"<{self.user_ref}@osap.account>"
        return clone


class DeliveryPort(Protocol):
    """Contrato mínimo que debe cumplir cualquier forma de entrega."""

    name: str

    def deliver(self, message: OutboundMessage) -> str | None:
        """Entrega el mensaje. Devuelve un identificador o None."""


class QueueDelivery:
    """Deja el mensaje en la tabla ``outbound_messages`` para que OSAP lo envíe."""

    name = "QUEUE"

    def __init__(self, connection) -> None:
        self.connection = connection

    def deliver(self, message: OutboundMessage) -> str | None:
        with self.connection.cursor() as cur:
            cur.execute(
                """INSERT INTO outbound_messages
                (user_ref, recipient, recipient_address, subject, body_text, body_html,
                 origin, kind, digest_date, digest_window_days, reference_id,
                 language_code, items_count, status, created_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'PENDING',UTC_TIMESTAMP(6))""",
                (
                    message.user_ref,
                    message.user_ref,
                    message.recipient_address,
                    message.subject,
                    message.body_text,
                    message.body_html,
                    message.origin,
                    message.kind,
                    message.digest_date,
                    message.digest_window_days,
                    message.reference,
                    message.language,
                    message.items,
                ),
            )
            message_id = int(cur.lastrowid)
        self.connection.commit()
        log.info("Mensaje %s encolado para %s", message_id, message.label)
        return str(message_id)


class FileDelivery:
    """Guarda el mensaje como ``.eml`` en un directorio."""

    name = "FILE"

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def deliver(self, message: OutboundMessage) -> str | None:
        safe = "".join(c if c.isalnum() or c in "-_@." else "_" for c in message.label)
        path = self.directory / f"{message.kind.lower()}_{safe}.eml"
        path.write_text(message.email_message_copy().as_string(), encoding="utf-8")
        log.info("Mensaje guardado en %s", path)
        return str(path)


def make_delivery(kind: str, connection, directory: str | Path = "var/outbound") -> DeliveryPort:
    kind = (kind or "QUEUE").upper()
    if kind == "FILE":
        return FileDelivery(directory)
    return QueueDelivery(connection)
