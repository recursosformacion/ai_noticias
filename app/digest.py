"""Proceso periódico del boletín: capturar y después enviar a cada suscriptor.

Es el trabajo que se ejecutará bajo cron (o un programador equivalente). Hace,
en este orden y de forma independiente:

1. **Captura** las fuentes activas (``ingest``). Si falla, el paso 2 puede seguir
   con lo que ya haya en la base: un fallo de red no debe impedir el envío del
   boletín pendiente.
2. **Recorre los usuarios de OSAP** con ``news_opt_in = 1`` (``osap_auth.users``),
   y para cada uno construye el resumen en su idioma y con sus temas.
3. **Deja cada mensaje en la cola** ``outbound_messages`` con su ``user_ref``.
   El envío real lo hace OSAP, que es quien conoce el buzón.

Garantías:

- **Idempotente por día**: si se ejecuta dos veces el mismo día, no reenvía el
  mismo boletín al mismo usuario (se comprueba ``digest_date``).
- **Un fallo no detiene el lote**: cada usuario se procesa de forma aislada.
- **Sin correos en claro**: nunca se escribe la dirección de un usuario real.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone

from .collector import ingest_active_channels
from .news_service import enqueue_response, process_request
from .mail_parser import NewsRequest
from .settings import ModuleSettings, load_settings
from .subscribers import (
    Subscriber,
    SubscriberError,
    all_topics,
    build_test_subscriber,
    list_subscribers,
)

log = logging.getLogger(__name__)


@dataclass
class SubscriberResult:
    user_ref: str
    name: str | None
    language: str
    topics: list[str]
    status: str
    items: int = 0
    message_id: str | None = None
    error: str | None = None

    def as_dict(self) -> dict:
        return {
            "user_ref": self.user_ref,
            "name": self.name,
            "language": self.language,
            "topics": self.topics,
            "status": self.status,
            "items": self.items,
            "message_id": self.message_id,
            "error": self.error,
        }


@dataclass
class DigestReport:
    started_at: str
    finished_at: str | None = None
    ingest_total_new: int = 0
    ingest_channels: int = 0
    ingest_errors: int = 0
    subscribers: int = 0
    queued: int = 0
    empty: int = 0
    skipped: int = 0
    failed: int = 0
    results: list[SubscriberResult] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "ingest": {
                "channels": self.ingest_channels,
                "new_items": self.ingest_total_new,
                "errors": self.ingest_errors,
            },
            "subscribers": self.subscribers,
            "queued": self.queued,
            "empty": self.empty,
            "skipped": self.skipped,
            "failed": self.failed,
            "notes": self.notes,
            "results": [r.as_dict() for r in self.results],
        }


def _topic_label_for_language(
    connection, code: str, labels: dict[str, str], language: str
) -> str:
    """Nombre del tema en el idioma pedido; si no hay traducción, el español."""
    if language != "es":
        with connection.cursor() as cur:
            cur.execute(
                """SELECT t.term FROM interest_topic_terms t
                JOIN interest_topics i ON i.id = t.interest_topic_id
                WHERE i.code = %s AND t.language_code = %s ORDER BY t.id LIMIT 1""",
                (code, language),
            )
            row = cur.fetchone()
            if row:
                return row["term"]
    return labels.get(code, code)


def _already_sent_today(connection, user_ref: str, digest_date: str) -> bool:
    """¿Este usuario ya tiene el boletín de hoy en la cola?"""
    with connection.cursor() as cur:
        cur.execute(
            """SELECT id FROM outbound_messages
            WHERE user_ref = %s AND digest_date = %s
              AND status IN ('PENDING', 'SENDING', 'SENT')
            LIMIT 1""",
            (user_ref, digest_date),
        )
        return cur.fetchone() is not None


def run_ingest(connection, settings: ModuleSettings) -> tuple[int, int, int]:
    """Paso 1: captura. Devuelve (canales, elementos nuevos, errores)."""
    try:
        results = ingest_active_channels(connection)
    except Exception as exc:  # noqa: BLE001 - el boletín debe continuar
        log.error("La captura falló: %s", exc)
        return 0, 0, 1

    new_items = sum(int(r.get("new", 0)) for r in results)
    errors = sum(int(r.get("error", 0)) for r in results) + sum(
        1 for r in results if r.get("status") == "FAILED"
    )
    return len(results), new_items, errors


def send_digest_for(
    subscriber: Subscriber,
    connection,
    settings: ModuleSettings,
    digest_date: str,
    window_days: int,
    delivery: str,
    topics: list[str] | None = None,
) -> SubscriberResult:
    """Construye y encola el boletín de un suscriptor."""
    chosen = topics if topics is not None else subscriber.topics
    request = NewsRequest(
        sender=subscriber.address or f"{subscriber.user_ref}@osap.account",
        sender_name=subscriber.name or "",
        subject="Boletín de noticias musicales",
        topics=chosen,
        language=subscriber.language,
    )

    response = process_request(
        request,
        connection,
        settings,
        build_message=True,
        limit=settings.max_items,
        window_days=window_days,
    )

    if not response.hits:
        # Se registra la consulta pero no se envía un correo vacío.
        return SubscriberResult(
            user_ref=subscriber.user_ref,
            name=subscriber.name,
            language=response.language,
            topics=chosen,
            status="EMPTY",
            items=0,
            message_id=None,
        )

    message_id = enqueue_response(
        response,
        connection,
        delivery_kind=delivery,
        directory=settings.mail.outbound_dir,
        user_ref=None if subscriber.address else subscriber.user_ref,
        recipient_address=subscriber.address,
        kind="NEWS_DIGEST",
        digest_date=digest_date,
        digest_window_days=window_days,
    )
    return SubscriberResult(
        user_ref=subscriber.user_ref,
        name=subscriber.name,
        language=response.language,
        topics=chosen,
        status="QUEUED",
        items=len(response.hits),
        message_id=message_id,
    )


def run_digest(
    connection,
    settings: ModuleSettings | None = None,
    do_ingest: bool = True,
    delivery: str | None = None,
    window_days: int | None = None,
    only_user: str | None = None,
    dry_run: bool = False,
    topics_override: list[str] | None = None,
    address_override: str | None = None,
    language_override: str | None = None,
) -> DigestReport:
    """Ejecuta el ciclo completo. Es lo que llamará el cron."""
    settings = settings or load_settings()
    delivery = (delivery or settings.mail.delivery).upper()
    window = window_days or settings.default_window_days
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    digest_date = now.date().isoformat()

    report = DigestReport(started_at=now.isoformat(timespec="seconds"))

    # 1) Captura
    if do_ingest:
        channels, new_items, errors = run_ingest(connection, settings)
        report.ingest_channels = channels
        report.ingest_total_new = new_items
        report.ingest_errors = errors
        if errors:
            report.notes.append(
                f"{errors} incidencia(s) durante la captura; el boletín usa lo ya almacenado."
            )

    # 2) Suscriptores
    if address_override:
        # En un envío manual se usan los nombres legibles de los temas, no sus códigos.
        from .subscribers import topic_labels

        labels = topic_labels(connection)
        codes = topics_override or list(labels)
        language = language_override or settings.default_language
        readable = [_topic_label_for_language(connection, c, labels, language) for c in codes]
        subscribers = [build_test_subscriber(address_override, language, readable)]
        report.notes.append(
            f"Envío manual a {address_override}: no se ha consultado la lista de usuarios de OSAP."
        )
    else:
        try:
            subscribers = list_subscribers(settings)
        except SubscriberError as exc:
            # Sin la lista real no se inventa nada: se anota y se termina.
            report.notes.append(f"No se pudo obtener la lista de suscriptores: {exc}")
            subscribers = []
        if not subscribers:
            report.notes.append(
                "No hay usuarios de OSAP con opt-in a noticias: no se genera ningún boletín."
            )

    if only_user:
        subscribers = [s for s in subscribers if s.user_ref == only_user]

    report.subscribers = len(subscribers)

    # 3) Un mensaje por suscriptor
    for subscriber in subscribers:
        try:
            if _already_sent_today(connection, subscriber.user_ref, digest_date):
                report.skipped += 1
                report.results.append(SubscriberResult(
                    user_ref=subscriber.user_ref,
                    name=subscriber.name,
                    language=subscriber.language,
                    topics=subscriber.topics,
                    status="ALREADY_SENT",
                ))
                continue

            if dry_run:
                report.results.append(SubscriberResult(
                    user_ref=subscriber.user_ref,
                    name=subscriber.name,
                    language=subscriber.language,
                    topics=topics_override or subscriber.topics,
                    status="DRY_RUN",
                ))
                continue

            result = send_digest_for(
                subscriber, connection, settings, digest_date, window, delivery,
                topics=topics_override,
            )
            report.results.append(result)
            if result.status == "QUEUED":
                report.queued += 1
            elif result.status == "EMPTY":
                report.empty += 1
        except Exception as exc:  # noqa: BLE001 - un usuario no detiene el lote
            log.exception("Error generando el boletín de %s", subscriber.user_ref)
            report.failed += 1
            report.results.append(SubscriberResult(
                user_ref=subscriber.user_ref,
                name=subscriber.name,
                language=subscriber.language,
                topics=subscriber.topics,
                status="FAILED",
                error=str(exc)[:500],
            ))

    finished = datetime.now(timezone.utc).replace(tzinfo=None)
    report.finished_at = finished.isoformat(timespec="seconds")
    return report
