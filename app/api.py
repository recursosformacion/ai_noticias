"""API interna de ai_noticias para OSAP.

Corrige la forma de acceso: **OSAP no envía correos a ai_noticias ni le pide la
lista de usuarios**. El usuario entra en OSAP, OSAP resuelve su identidad y sus
preferencias, y consulta aquí solo con `language` + `topics`.

Esta API:
- no lee ni escribe perfiles de usuario;
- no envía correo ni usa `outbound_messages`;
- no expone direcciones de correo;
- solo devuelve noticias del corpus y el catálogo temático.

Autenticación de servicio: cabecera `X-OSAP-News-Token`, comparada en tiempo
constante con `OSAP_NEWS_API_TOKEN`. Sin token configurado la API falla cerrada.
"""
from __future__ import annotations

import logging
import secrets

from fastapi import FastAPI, Header, HTTPException, Query

from .db import connect
from .news_service import RequestRejected, list_topics, query_news
from .settings import LANGS, load_settings

log = logging.getLogger(__name__)

app = FastAPI(
    title="ai_noticias internal API",
    version="0.2.0",
    description="Consulta de noticias para OSAP. Sin usuarios, correo ni colas de salida.",
)


def _require_token(token: str | None) -> None:
    expected = load_settings().api_token
    if not expected:
        raise HTTPException(status_code=503, detail="OSAP_NEWS_API_TOKEN no configurado")
    if not token or not secrets.compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="token de servicio inválido")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai_noticias"}


@app.get("/api/v1/news/topics")
def topics(x_osap_news_token: str | None = Header(default=None)) -> dict[str, object]:
    _require_token(x_osap_news_token)
    connection = connect()
    try:
        items = list_topics(connection)
    finally:
        connection.close()
    return {"items": items, "count": len(items)}


@app.get("/api/v1/news")
def news(
    language: str = Query("es"),
    languages: str = Query(""),
    topics: str = Query(""),
    limit: int = Query(20, ge=1, le=100),
    days: int = Query(30, ge=1, le=3650),
    x_osap_news_token: str | None = Header(default=None),
) -> dict[str, object]:
    _require_token(x_osap_news_token)
    requested_languages = [
        part.strip().lower() for part in (languages or language or "es").split(",")
        if part.strip()
    ]
    requested_languages = list(dict.fromkeys(requested_languages)) or ["es"]
    unsupported = [item for item in requested_languages if item not in LANGS]
    if unsupported:
        raise HTTPException(status_code=400, detail=f"idioma no soportado: {unsupported[0]}")
    selected_topics = [part.strip() for part in (topics or "").split(",") if part.strip()]

    connection = connect()
    try:
        responses = [
            query_news(
                connection,
                load_settings(),
                topics=selected_topics,
                language=language_code,
                limit=limit,
                window_days=days,
            )
            for language_code in requested_languages
        ]
    except RequestRejected as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        log.exception("consulta de noticias fallida")
        raise HTTPException(status_code=503, detail="corpus de noticias no disponible") from exc
    finally:
        connection.close()

    seen: set[object] = set()
    items: list[dict[str, object]] = []
    for response in responses:
        for hit in response.hits:
            item = hit.as_dict()
            key = item.get("news_item_id") or item.get("url") or item.get("title")
            if key in seen:
                continue
            seen.add(key)
            items.append(item)
    items.sort(key=lambda item: str(item.get("published_at") or ""), reverse=True)
    items = items[:limit]
    return {
        "items": items,
        "count": len(items),
        "language": requested_languages[0],
        "languages": requested_languages,
        "topics": sorted({label for response in responses for label in response.topics}),
        "window_days": days,
    }


def main() -> None:
    import uvicorn

    uvicorn.run("app.api:app", host="127.0.0.1", port=8401)


if __name__ == "__main__":
    main()



