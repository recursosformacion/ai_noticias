"""Catálogo musical de OSAP, obtenido **por API**.

``ai_noticias`` no abre conexiones a ``osap_storage`` ni a ``osap_api``: el
vocabulario controlado (géneros) y la búsqueda de obras se piden a
``osap-api`` (``GET /api/v1/genres`` y ``GET /api/v1/search/works``).

El resultado se cachea en memoria durante la ejecución porque el proceso cron
atiende a muchos usuarios seguidos y no tiene sentido repetir la misma llamada
para cada uno.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field

from .osap_api import OsapApiError, OsapClient
from .settings import ModuleSettings

log = logging.getLogger(__name__)


@dataclass
class OsapVocabulary:
    """Vocabulario musical disponible para expandir los temas de interés."""

    genres: dict[str, str] = field(default_factory=dict)  # id -> nombre
    available: bool = False
    error: str | None = None

    def genre_names(self, ids) -> list[str]:
        result = []
        for gid in ids or ():
            name = self.genres.get(str(gid))
            if name:
                result.append(name)
        return result

    def as_dict(self) -> dict:
        return {
            "available": self.available,
            "error": self.error,
            "genres": len(self.genres),
            "sample": list(self.genres.values())[:8],
        }


def make_client(settings: ModuleSettings) -> OsapClient:
    return OsapClient(
        base_url=settings.catalog_api_url,
        auth_url=settings.catalog_api_url,
        service_email=settings.service_email,
        service_password=settings.service_password,
        token=settings.catalog_token,
        timeout=settings.api_timeout,
    )


def load_vocabulary(
    settings: ModuleSettings,
    client: OsapClient | None = None,
) -> OsapVocabulary:
    """Carga los géneros desde la API. Nunca lanza: devuelve ``available=False``."""
    vocab = OsapVocabulary()
    if not settings.api_enabled:
        vocab.error = "API de OSAP deshabilitada en la configuración"
        return vocab

    client = client or make_client(settings)
    try:
        genres = client.genres()
    except OsapApiError as exc:
        vocab.error = str(exc)
        log.warning("No se pudo cargar el catálogo de géneros: %s", exc)
        return vocab

    for genre in genres:
        gid = genre.get("id") or genre.get("genre_id")
        name = genre.get("name") or genre.get("genre_name") or genre.get("title")
        if gid is not None and name:
            vocab.genres[str(gid)] = str(name)
    vocab.available = bool(vocab.genres)
    return vocab


def search_works(
    settings: ModuleSettings,
    term: str,
    limit: int = 5,
    client: OsapClient | None = None,
) -> list[dict]:
    """Busca obras por título o compositor en la API de OSAP."""
    client = client or make_client(settings)
    try:
        return client.search_works(term, limit)
    except OsapApiError as exc:
        log.warning("Búsqueda de obras «%s» fallida: %s", term, exc)
        return []
