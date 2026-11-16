"""Configuración del módulo de correo.

Lee `osap.toml` y permite sobreescribir por variables de entorno. No contiene
credenciales de correo: el envío lo realiza OSAP (`osap-support`) y este módulo
solo firma el mensaje con los datos de remitente.
"""
from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "osap.toml"

LANGS = {"es": "Español", "en": "English", "fr": "Français", "de": "Deutsch",
         "it": "Italiano", "pt": "Português", "ca": "Català"}


@dataclass(frozen=True)
class MailSettings:
    """Identidad del remitente.

    IMPORTANTE: aquí **no** hay servidor SMTP. El envío corresponde a OSAP
    (`osap-support`), que es quien gestiona las comunicaciones (ADR-006). Este
    módulo solo firma el mensaje con estos datos y lo deja en la cola.
    """

    from_address: str = "noticias@osap.local"
    from_name: str = "OSAP Noticias"
    reply_to: str | None = None
    # Destino de la entrega: QUEUE (tabla outbound_messages) o FILE (disco).
    delivery: str = "QUEUE"
    outbound_dir: str = "var/outbound"


@dataclass(frozen=True)
class ModuleSettings:
    default_language: str = "es"
    max_items: int = 20
    default_window_days: int = 365
    allowed_senders: tuple[str, ...] = ()
    allowed_domains: tuple[str, ...] = ()

    # Token compartido para la API interna de consulta (OSAP -> ai_noticias).
    # No se usa para correo ni para leer usuarios: la API solo devuelve noticias.
    api_token: str | None = None

    # --- APIs de OSAP (nunca conexión directa a otras bases) ---
    api_enabled: bool = True
    # Identidad y preferencias de usuario (osap-auth).
    identity_api_url: str = "http://127.0.0.1:8001"
    identity_token: str | None = None
    # Catálogo musical (osap-api).
    catalog_api_url: str = "http://127.0.0.1:8000"
    catalog_token: str | None = None
    # Credenciales de servicio para obtener token (login máquina a máquina).
    service_email: str | None = None
    service_password: str | None = None
    api_timeout: float = 10.0

    mail: MailSettings = field(default_factory=MailSettings)


def _env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    return value if value not in (None, "") else default


def _flag(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "si", "sí", "on"}


def _csv(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(item.strip().lower() for item in value.split(",") if item.strip())


def load_raw() -> dict:
    if not CONFIG_PATH.is_file():
        return {}
    with CONFIG_PATH.open("rb") as handle:
        return tomllib.load(handle)


def load_settings() -> ModuleSettings:
    raw = load_raw()
    db = raw.get("db") or {}
    mail_raw = raw.get("mail") or {}
    news = raw.get("noticias") or {}
    osap = raw.get("osap") or {}

    default_language = (_env("OSAP_NEWS_LANG", news.get("default_language")) or "es").lower()
    if default_language not in LANGS:
        default_language = "es"

    # Sin SMTP: solo identidad del remitente y destino de la entrega.
    mail = MailSettings(
        from_address=_env("OSAP_NEWS_MAIL_FROM", mail_raw.get("from_address"))
        or "noticias@osap.local",
        from_name=_env("OSAP_NEWS_MAIL_FROM_NAME", mail_raw.get("from_name"))
        or "OSAP Noticias",
        reply_to=_env("OSAP_NEWS_MAIL_REPLY_TO", mail_raw.get("reply_to")),
        delivery=(_env("OSAP_NEWS_DELIVERY", mail_raw.get("delivery")) or "QUEUE").upper(),
        outbound_dir=_env("OSAP_NEWS_OUTBOUND_DIR", mail_raw.get("outbound_dir"))
        or "var/outbound",
    )

    apis = raw.get("apis") or {}
    identity = apis.get("identity") or {}
    catalog = apis.get("catalog") or {}

    return ModuleSettings(
        api_token=_env("OSAP_NEWS_API_TOKEN", (raw.get("api") or {}).get("token")),
        default_language=default_language,
        max_items=int(_env("OSAP_NEWS_MAX_ITEMS", str(news.get("max_items") or 20))),
        default_window_days=int(
            _env("OSAP_NEWS_WINDOW_DAYS", str(news.get("window_days") or 30))
        ),
        allowed_senders=_csv(_env("OSAP_NEWS_ALLOWED_SENDERS", news.get("allowed_senders"))),
        allowed_domains=_csv(_env("OSAP_NEWS_ALLOWED_DOMAINS", news.get("allowed_domains"))),
        api_enabled=_flag("OSAP_NEWS_API_ENABLED", bool(apis.get("enabled", True))),
        identity_api_url=(
            _env("OSAP_NEWS_IDENTITY_API_URL", identity.get("url"))
            or "http://127.0.0.1:8001"
        ).rstrip("/"),
        identity_token=_env("OSAP_NEWS_IDENTITY_TOKEN", identity.get("token")),
        catalog_api_url=(
            _env("OSAP_NEWS_CATALOG_API_URL", catalog.get("url"))
            or "http://127.0.0.1:8000"
        ).rstrip("/"),
        catalog_token=_env("OSAP_NEWS_CATALOG_TOKEN", catalog.get("token")),
        service_email=_env("OSAP_NEWS_SERVICE_EMAIL", apis.get("service_email")),
        service_password=_env("OSAP_NEWS_SERVICE_PASSWORD", apis.get("service_password")),
        api_timeout=float(_env("OSAP_NEWS_API_TIMEOUT", str(apis.get("timeout") or 10))),
        mail=mail,
    )
