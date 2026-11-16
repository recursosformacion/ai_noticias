"""Suscriptores del boletín: los usuarios de OSAP, obtenidos **por API**.

Regla de arquitectura
---------------------

``ai_noticias`` solo lee su propia base (``osap_noticias``). Los usuarios y sus
preferencias viven en ``osap-auth`` y se consultan a través de
``GET /api/v1/admin/users``, que devuelve:

- ``id``            → identificador de la cuenta (``user_ref`` en la cola).
- ``email``         → dirección de contacto.
- ``news_opt_in``   → solo se envía si es verdadero.
- ``news_language`` → idioma del resumen.
- ``news_topics``   → temas de interés del usuario.

No hay ninguna conexión directa a la base de identidad: si la API no responde,
el proceso lo anota y no envía, en lugar de leer la tabla por su cuenta.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from .osap_api import OsapApiError, OsapClient
from .settings import ModuleSettings

log = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = {"es", "en", "fr", "de", "it", "pt", "ca"}


@dataclass
class Subscriber:
    user_ref: str
    name: str | None
    language: str
    topics: list[str] = field(default_factory=list)
    # Dirección de envío. En producción llega desde la API de identidad.
    address: str | None = None
    # Marca de origen: API, prueba manual o fichero.
    source: str = "API"

    def as_dict(self) -> dict:
        return {
            "user_ref": self.user_ref,
            "name": self.name,
            "language": self.language,
            "topics": self.topics,
            "source": self.source,
            "has_address": bool(self.address),
        }


class SubscriberError(RuntimeError):
    """No se pudo obtener la lista de suscriptores."""


def _parse_topics(value) -> list[str]:
    """Acepta lista, JSON o cadena separada por comas."""
    if not value:
        return []
    if isinstance(value, (list, tuple)):
        return [str(t).strip() for t in value if str(t).strip()]
    text = str(value).strip()
    if text.startswith("["):
        try:
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(t).strip() for t in parsed if str(t).strip()]
        except (TypeError, ValueError):
            pass
    return [part.strip() for part in text.split(",") if part.strip()]


def _is_opted_in(user: dict) -> bool:
    value = user.get("news_opt_in", user.get("newsOptIn"))
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "si", "sí", "on"}


def _make_client(settings: ModuleSettings) -> OsapClient:
    return OsapClient(
        base_url=settings.identity_api_url,
        auth_url=settings.identity_api_url,
        service_email=settings.service_email,
        service_password=settings.service_password,
        token=settings.identity_token,
        timeout=settings.api_timeout,
    )


def list_subscribers(
    settings: ModuleSettings,
    client: OsapClient | None = None,
) -> list[Subscriber]:
    """Usuarios con opt-in a noticias, en su idioma y con sus temas.

    Lanza :class:`SubscriberError` si la API de identidad no responde: es preferible
    un fallo visible a enviar (o no enviar) silenciosamente por una lista incompleta.
    """
    client = client or _make_client(settings)
    try:
        users = client.list_users()
    except OsapApiError as exc:
        raise SubscriberError(f"No se pudo leer la lista de usuarios: {exc}") from exc

    subscribers: list[Subscriber] = []
    for user in users:
        if not _is_opted_in(user):
            continue
        status = str(user.get("status") or "active").lower()
        if status != "active":
            continue
        address = (user.get("email") or "").strip()
        if not address:
            log.warning("Usuario %s sin correo en la API: se omite", user.get("id"))
            continue

        language = str(user.get("news_language") or settings.default_language).lower()
        if language not in SUPPORTED_LANGUAGES:
            language = settings.default_language

        topics = _parse_topics(user.get("news_topics"))
        subscribers.append(Subscriber(
            user_ref=str(user.get("id")),
            name=user.get("name"),
            language=language,
            topics=topics,
            address=address,
            source="API",
        ))
    return subscribers


def all_topics(connection) -> list[str]:
    """Todos los temas semilla definidos en ``osap_noticias`` (base propia)."""
    with connection.cursor() as cur:
        cur.execute("SELECT code FROM interest_topics WHERE status='ACTIVE' ORDER BY id")
        return [r["code"] for r in cur.fetchall()]


def topic_labels(connection) -> dict[str, str]:
    """Código → nombre legible de los temas semilla."""
    with connection.cursor() as cur:
        cur.execute("SELECT code, name FROM interest_topics WHERE status='ACTIVE' ORDER BY id")
        return {r["code"]: r["name"] for r in cur.fetchall()}


def build_test_subscriber(
    address: str,
    language: str,
    topics: list[str],
    name: str | None = None,
) -> Subscriber:
    """Suscriptor sintético para pruebas manuales con una dirección concreta."""
    return Subscriber(
        user_ref="TEST-MANUAL",
        name=name,
        language=language,
        topics=topics,
        address=address.strip().lower(),
        source="TEST",
    )
