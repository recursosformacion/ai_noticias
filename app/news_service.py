"""Servicio que responde a un correo con una lista de noticias por temas e idioma.

Es el punto de entrada del módulo y no depende del transporte: recibe un mensaje
(``email.message.Message``) o los parámetros ya extraídos, y devuelve un
:class:`NewsResponse` con el correo de respuesta construido.

Resolución de temas (orden de prioridad):

1. **Perfil del usuario** (``user_profiles`` + ``user_topics``), si el remitente está
   registrado. Sus temas y su idioma preferido mandan.
2. **Petición en el correo**, si no hay perfil o si el usuario pide temas concretos
   de forma explícita (``temas:`` en el cuerpo). Así el usuario no está atado
   al perfil y puede hacer consultas puntuales.
3. Si no hay ni perfil ni temas, se responde con la actualidad general del idioma.

El servicio escribe la traza en ``email_requests`` / ``email_request_items`` y nunca
expone el correo en claro en esos registros.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from email import policy
from email.message import Message
from email.parser import BytesParser

from . import profiles as profiles_repo
from .mail_builder import build_reply
from .mail_parser import NewsRequest, parse_message, parse_topics
from .news_search import (
    NewsHit,
    TopicResolution,
    load_seed_topics,
    resolve_topic,
    search_news,
)
from .osap_catalog import OsapVocabulary, load_vocabulary
from .settings import LANGS, ModuleSettings, load_settings

log = logging.getLogger(__name__)


class RequestRejected(Exception):
    """Petición inválida: remitente no autorizado o idioma no soportado."""


@dataclass
class NewsResponse:
    request: NewsRequest
    topics: list[str]
    language: str
    hits: list[NewsHit]
    resolutions: list[TopicResolution] = field(default_factory=list)
    profile: profiles_repo.UserProfile | None = None
    topic_source: str = "EMAIL"
    warnings: list[str] = field(default_factory=list)
    message: Message | None = None
    request_id: int | None = None
    status: str = "OK"

    def as_dict(self) -> dict:
        return {
            "status": self.status,
            "request_id": self.request_id,
            "sender": self.request.sender,
            "subject": self.request.subject,
            "topics": self.topics,
            "language": self.language,
            "language_name": LANGS.get(self.language, self.language),
            "topic_source": self.topic_source,
            "profile": self.profile.as_dict() if self.profile else None,
            "resolutions": [r.as_dict() for r in self.resolutions],
            "count": len(self.hits),
            "items": [h.as_dict() for h in self.hits],
            "warnings": self.warnings,
        }


# --------------------------------------------------------------------------- #
# Validación de remitente
# --------------------------------------------------------------------------- #

def check_sender(address: str, settings: ModuleSettings) -> None:
    """Aplica lista blanca de remitentes o dominios, si está configurada."""
    address = (address or "").strip().lower()
    if not address or "@" not in address:
        raise RequestRejected("El correo no tiene un remitente válido.")
    if not settings.allowed_senders and not settings.allowed_domains:
        return
    domain = address.split("@", 1)[1]
    if address in settings.allowed_senders:
        return
    if settings.allowed_domains and any(
        domain == d or domain.endswith("." + d) for d in settings.allowed_domains
    ):
        return
    raise RequestRejected(
        "El remitente no está autorizado para consultar el servicio de noticias."
    )


# --------------------------------------------------------------------------- #
# Composición de la consulta
# --------------------------------------------------------------------------- #

def _resolutions_from_profile(
    profile: profiles_repo.UserProfile,
    language: str,
    seeds: list[dict],
    vocabulary: OsapVocabulary,
) -> tuple[list[TopicResolution], list[str]]:
    resolutions: list[TopicResolution] = []
    labels: list[str] = []
    for topic in profile.topics_for_language(language):
        base = topic.label
        resolution = resolve_topic(base, seeds, vocabulary, language=language)
        # El peso del tema en el perfil modula la puntuación de las coincidencias.
        resolution.weight = max(0.1, min(float(topic.weight or 1.0), 5.0))
        # Los términos propios del usuario tienen prioridad sobre la expansión automática.
        extra = [k for k in topic.keywords if k and k.lower() not in {x.lower() for x in resolution.keywords}]
        resolution.keywords = list(dict.fromkeys([*extra, *resolution.keywords]))
        resolutions.append(resolution)
        labels.append(base)
    return resolutions, labels


def _resolutions_from_request(
    request: NewsRequest,
    seeds: list[dict],
    vocabulary: OsapVocabulary,
    language: str,
) -> tuple[list[TopicResolution], list[str]]:
    resolutions = [
        resolve_topic(t, seeds, vocabulary, language=language) for t in request.topics
    ]
    return resolutions, list(request.topics)


def prepare(
    request: NewsRequest,
    connection,
    settings: ModuleSettings,
    vocabulary: OsapVocabulary | None = None,
) -> tuple[list[TopicResolution], list[str], str, profiles_repo.UserProfile | None, str]:
    """Decide qué temas e idioma se usan. Devuelve (resoluciones, etiquetas, idioma, perfil, origen)."""
    vocabulary = vocabulary or load_vocabulary(settings)
    seeds = load_seed_topics(connection)

    profile = profiles_repo.get_profile_by_email(connection, request.sender)
    explicit_topics = bool(request.topics) and bool(
        request.headers.get("X-Osap-Topics") or "temas:" in request.raw_body.lower()
    )

    if profile and profile.is_active and not explicit_topics:
        language = profile.preferred_language or settings.default_language
        if request.headers.get("X-Osap-Language") or request.language != settings.default_language:
            # El usuario puede pedir otro idioma explícitamente en el correo.
            language = request.language
        resolutions, labels = _resolutions_from_profile(profile, language, seeds, vocabulary)
        if not labels:
            resolutions, labels = _resolutions_from_request(request, seeds, vocabulary, language)
        return resolutions, labels, language, profile, "PROFILE"

    language = request.language or settings.default_language
    if profile and profile.is_active and explicit_topics and profile.preferred_language:
        language = request.language or profile.preferred_language
    resolutions, labels = _resolutions_from_request(request, seeds, vocabulary, language)
    return resolutions, labels, language, profile, "EMAIL"


# --------------------------------------------------------------------------- #
# Traza en base de datos
# --------------------------------------------------------------------------- #

def _record_request(
    connection,
    request: NewsRequest,
    response: NewsResponse,
    limit: int,
    window_days: int,
) -> int:
    import json

    # Idempotencia: si el mismo Message-ID ya se procesó (reintento del MTA o
    # reprocesamiento de la carpeta), se reutiliza el registro previo.
    if request.message_id:
        with connection.cursor() as cur:
            cur.execute(
                "SELECT id FROM email_requests WHERE message_id=%s",
                (request.message_id[:255],),
            )
            existing = cur.fetchone()
        if existing:
            log.info("Mensaje %s ya procesado (id %s)", request.message_id, existing["id"])
            return int(existing["id"])

    with connection.cursor() as cur:
        cur.execute(
            """INSERT INTO email_requests
            (profile_id, message_id, sender_hash, sender_domain, subject, topics_json,
             topic_source, languages_json, limit_requested, window_days, result_status,
             items_sent, response_subject, received_at, processed_at)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,UTC_TIMESTAMP(6),UTC_TIMESTAMP(6))""",
            (
                response.profile.id if response.profile else None,
                (request.message_id or "")[:255] or None,
                profiles_repo.email_lookup(request.sender or ""),
                (request.sender.split("@")[-1] if "@" in (request.sender or "") else None),
                (request.subject or "")[:500],
                json.dumps(response.topics, ensure_ascii=False),
                response.topic_source,
                json.dumps([response.language], ensure_ascii=False),
                limit,
                window_days,
                response.status,
                len(response.hits),
                (response.message.get("Subject") if response.message else None),
            ),
        )
        request_id = int(cur.lastrowid)
        for position, hit in enumerate(response.hits, start=1):
            cur.execute(
                """INSERT INTO email_request_items
                (email_request_id, news_item_id, publication_id, rank_position, score, matched_terms)
                VALUES (%s,%s,%s,%s)""",
                (
                    request_id,
                    hit.news_item_id,
                    hit.publication_id,
                    position,
                    hit.score,
                    ", ".join(hit.matched)[:1000],
                ),
            )
    if response.profile:
        profiles_repo.mark_request(connection, response.profile.id)
    return request_id


# --------------------------------------------------------------------------- #
# Consulta de la API interna de OSAP
# --------------------------------------------------------------------------- #

def list_topics(connection) -> list[dict[str, str]]:
    """Catálogo temático para la API interna (sin datos de usuario)."""
    return [
        {
            "code": str(topic["code"]),
            "name": str(topic["name"]),
            "description": str(topic.get("description") or ""),
        }
        for topic in load_seed_topics(connection)
    ]


def query_news(
    connection,
    settings: ModuleSettings,
    *,
    topics: list[str],
    language: str,
    limit: int = 20,
    window_days: int = 30,
) -> NewsResponse:
    """Consulta noticias para OSAP usando **solo temas e idioma**.

    No hay remitente, perfil, consentimiento ni cola de correo: la identidad y las
    preferencias las resuelve OSAP antes de llamar. Esta función no escribe en la BD.
    """
    if language not in LANGS:
        raise RequestRejected(f"Idioma no soportado: {language}")

    vocabulary = load_vocabulary(settings)
    seeds = load_seed_topics(connection)
    selected = list(topics) or [str(topic["code"]) for topic in seeds]
    request = NewsRequest(topics=selected, language=language)
    resolutions, labels = _resolutions_from_request(request, seeds, vocabulary, language)
    hits = search_news(
        connection,
        resolutions,
        language=language,
        limit=max(1, min(int(limit), 100)),
        window_days=max(1, min(int(window_days), 3650)),
    )
    return NewsResponse(
        request=request,
        topics=labels,
        language=language,
        hits=hits,
        resolutions=resolutions,
        topic_source="OSAP",
        status="OK" if hits else "EMPTY",
    )


# --------------------------------------------------------------------------- #
# API principal
# --------------------------------------------------------------------------- #

def process_request(
    request: NewsRequest,
    connection,
    settings: ModuleSettings | None = None,
    vocabulary: OsapVocabulary | None = None,
    build_message: bool = True,
    limit: int | None = None,
    window_days: int | None = None,
) -> NewsResponse:
    """Resuelve una petición y prepara la respuesta.

    ``limit`` y ``window_days`` permiten forzar valores desde la línea de comandos
    o desde otro servicio, por encima de los del mensaje y del perfil.
    """
    settings = settings or load_settings()

    check_sender(request.sender, settings)
    if request.language not in LANGS:
        raise RequestRejected(f"Idioma no soportado: {request.language}")

    resolutions, labels, language, profile, topic_source = prepare(
        request, connection, settings, vocabulary
    )

    limit = limit or request.limit or (profile.max_items if profile else settings.max_items)
    limit = max(1, min(int(limit), settings.max_items * 5, 100))
    window = (
        window_days
        or request.window_days
        or (profile.window_days if profile else settings.default_window_days)
    )

    hits = search_news(
        connection,
        resolutions,
        language=language,
        limit=limit,
        window_days=window,
    )

    warnings = list(request.warnings)
    if not hits:
        warnings.append(
            f"Sin resultados para los temas e idioma solicitados en la ventana de {window} días."
        )
    # Solo se avisa cuando de verdad se esperaba un perfil (consulta recibida por
    # correo). En un envío manual o desde la API el origen es el propio peticionario.
    if (
        topic_source == "EMAIL"
        and not profile
        and request.sender
        and "@" in request.sender
        and not request.subject.startswith(("Boletín", "Consulta directa"))
    ):
        warnings.append(
            "No hay un perfil registrado para este correo; los temas se han tomado del mensaje."
        )

    response = NewsResponse(
        request=request,
        topics=labels,
        language=language,
        hits=hits,
        resolutions=resolutions,
        profile=profile,
        topic_source=topic_source,
        warnings=warnings,
        status="OK" if hits else "EMPTY",
    )

    if build_message:
        # El mensaje se construye aquí, pero NO se envía: se entrega a la cola para
        # que OSAP (osap-support) lo envíe. Ver app/delivery.py y ADR-006.
        response.message = build_reply(
            to_address=request.sender,
            hits=hits,
            topics=labels,
            language=language,
            from_address=settings.mail.from_address,
            from_name=settings.mail.from_name,
            reply_to=settings.mail.reply_to,
            in_reply_to=request.message_id,
            warnings=warnings,
            recipient_name=(profile.display_name if profile else request.sender_name) or None,
            from_profile=topic_source == "PROFILE",
        )

    return response


def handle_raw_message(
    raw: str | bytes,
    connection,
    settings: ModuleSettings | None = None,
    persist: bool = True,
    build_message: bool = True,
    limit: int | None = None,
    window_days: int | None = None,
) -> NewsResponse:
    """Punto de entrada para un correo en bruto (texto o bytes RFC 822)."""
    settings = settings or load_settings()
    # Siempre por bytes: un mensaje recibido es una secuencia de octetos y es el
    # propio correo (charset del Content-Type) quien declara su codificación. Pasar
    # una cadena hace que email la recodifique y corrompe los acentos.
    if isinstance(raw, str):
        raw = raw.encode("utf-8")
    # policy.default decodifica correctamente cabeceras con acentos (RFC 2047 y
    # UTF-8 sin codificar); con la política "compat32" acaban en mojibake.
    message = BytesParser(policy=policy.default).parsebytes(raw)
    request = parse_message(message, settings.default_language)

    try:
        response = process_request(
            request, connection, settings, build_message=build_message,
            limit=limit, window_days=window_days,
        )
    except RequestRejected as exc:
        response = NewsResponse(
            request=request,
            topics=request.topics,
            language=request.language,
            hits=[],
            status="REJECTED",
            warnings=[str(exc)],
        )
        # No se responde a un remitente no autorizado: contestar a cualquier dirección
        # convierte el servicio en un relé de spam y revela que existe.
        response.message = None
        if persist:
            _record_request(connection, request, response, 0, 0)
        connection.commit()
        return response

    if persist:
        limit = request.limit or settings.max_items
        window = request.window_days or settings.default_window_days
        response.request_id = _record_request(connection, request, response, limit, window)
        connection.commit()

    return response


def handle_topics(
    sender: str,
    topics: list[str],
    language: str = "es",
    limit: int | None = None,
    window_days: int | None = None,
    connection=None,
    settings: ModuleSettings | None = None,
    build_message: bool = False,
) -> NewsResponse:
    """API directa (sin correo) para pruebas y para otros servicios de OSAP."""
    settings = settings or load_settings()
    request = NewsRequest(
        sender=sender,
        subject="Consulta directa",
        topics=parse_topics(", ".join(topics)) if len(topics) == 1 else topics,
        language=language,
    )
    if connection is None:
        from .db import connect

        connection = connect()
        try:
            return process_request(
                request, connection, settings, build_message=build_message,
                limit=limit, window_days=window_days,
            )
        finally:
            connection.close()
    return process_request(
        request, connection, settings, build_message=build_message,
        limit=limit, window_days=window_days,
    )


def enqueue_response(
    response: NewsResponse,
    connection,
    delivery_kind: str = "QUEUE",
    directory: str = "var/outbound",
    user_ref: str | None = None,
    recipient_address: str | None = None,
    kind: str = "NEWS_DIGEST",
    digest_date: str | None = None,
    digest_window_days: int | None = None,
) -> str | None:
    """Entrega el mensaje de respuesta al puerto de salida (no envía correo).

    Por defecto lo deja en ``outbound_messages`` para que OSAP lo envíe. Con
    ``delivery_kind='FILE'`` lo escribe en disco, útil en desarrollo.

    El destinatario se identifica por ``user_ref`` (cuenta de OSAP) o, en pruebas,
    por ``recipient_address``. Nunca se guarda el correo de un usuario real.
    """
    from .delivery import OutboundMessage, make_delivery

    if response.message is None:
        return None
    message = response.message
    outbound = OutboundMessage(
        subject=str(message.get("Subject") or ""),
        body_text=_extract_body(message, "plain"),
        body_html=_extract_body(message, "html"),
        message=message,
        user_ref=user_ref,
        recipient_address=recipient_address,
        kind=kind,
        origin="AI_NOTICIAS",
        reference=str(response.request_id) if response.request_id else None,
        language=response.language,
        items=len(response.hits),
        digest_date=digest_date,
        digest_window_days=digest_window_days,
    )
    return make_delivery(delivery_kind, connection, directory).deliver(outbound)


def _extract_body(message, subtype: str) -> str:
    """Extrae la parte text/plain o text/html de un mensaje multipart."""
    if not message.is_multipart():
        return message.get_payload(decode=True).decode(
            message.get_content_charset() or "utf-8", "replace"
        )
    for part in message.walk():
        if part.get_content_type() == f"text/{subtype}":
            payload = part.get_payload(decode=True) or b""
            return payload.decode(part.get_content_charset() or "utf-8", "replace")
    return ""


def describe_vocabulary(settings: ModuleSettings | None = None) -> dict:
    """Resumen del catálogo musical obtenido por API (diagnóstico)."""
    settings = settings or load_settings()
    vocab = load_vocabulary(settings)
    return {
        "source": settings.catalog_api_url + "/api/v1/genres",
        **vocab.as_dict(),
    }


