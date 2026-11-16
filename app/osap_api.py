"""Cliente HTTP de las APIs de OSAP.

Regla de arquitectura de este módulo: **ai_noticias solo lee su propia base**
(``osap_noticias``). Todo lo que viva en otra base se pide por API:

- Identidad y preferencias del usuario → ``osap-auth`` ``/api/v1/admin/users``
  (devuelve ``email``, ``news_opt_in``, ``news_language`` y ``news_topics``).
- Catálogo musical → ``osap-api`` ``/api/v1/genres`` (y búsqueda de obras).

Detalles de transporte:

- Autenticación por ``Authorization: Bearer <token>``. El token se obtiene con
  las credenciales de servicio configuradas y se cachea hasta que caduca.
- Reintentos con espera progresiva ante errores 5xx o de red.
- Timeout corto: un servicio caído no debe bloquear el proceso cron.
- Errores nunca incluyen el token ni la contraseña en el mensaje.
"""
from __future__ import annotations

import json
import logging
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field

log = logging.getLogger(__name__)


class OsapApiError(RuntimeError):
    """Error de comunicación o de autenticación con una API de OSAP."""


@dataclass
class ApiToken:
    value: str
    expires_at: float = 0.0

    @property
    def valid(self) -> bool:
        # 60 s de margen para no enviar un token a punto de caducar.
        return bool(self.value) and time.time() < self.expires_at - 60


@dataclass
class OsapClient:
    """Cliente sencillo (stdlib) para las APIs internas de OSAP."""

    base_url: str
    timeout: float = 10.0
    token: str | None = None
    # Credenciales de servicio para obtener token (login máquina a máquina).
    auth_url: str | None = None
    service_email: str | None = None
    service_password: str | None = None
    user_agent: str = "ai_noticias/0.1"
    _token: ApiToken = field(default_factory=lambda: ApiToken(""), repr=False)

    # ------------------------------------------------------------------ #
    # Transporte
    # ------------------------------------------------------------------ #

    def _request(self, method: str, url: str, payload: dict | None = None,
                 token: str | None = None, retries: int = 2) -> dict:
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        headers = {"Accept": "application/json", "User-Agent": self.user_agent}
        if data is not None:
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = f"Bearer {token}"

        last_error = None
        for attempt in range(retries + 1):
            request = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as response:
                    body = response.read()
                return json.loads(body) if body else {}
            except urllib.error.HTTPError as exc:
                detail = ""
                try:
                    detail = exc.read().decode("utf-8", "replace")[:200]
                except Exception:
                    pass
                if exc.code in (401, 403):
                    raise OsapApiError(
                        f"{url} devolvió {exc.code}: credenciales o permisos insuficientes"
                    ) from exc
                if exc.code == 404:
                    raise OsapApiError(f"{url} no existe (404)") from exc
                last_error = f"HTTP {exc.code} {detail}"
                if exc.code < 500:
                    break
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                last_error = f"error de red: {exc}"
            except json.JSONDecodeError as exc:
                raise OsapApiError(f"{url} no devolvió JSON válido") from exc
            if attempt < retries:
                time.sleep(0.5 * (attempt + 1))
        raise OsapApiError(f"{url}: {last_error}")

    # ------------------------------------------------------------------ #
    # Autenticación
    # ------------------------------------------------------------------ #

    def _get_token(self) -> str | None:
        if self.token:
            return self.token
        if self._token.valid:
            return self._token.value
        if not (self.auth_url and self.service_email and self.service_password):
            return None
        data = self._request(
            "POST",
            f"{self.auth_url.rstrip('/')}/api/v1/login",
            {"email": self.service_email, "password": self.service_password},
        )
        token = data.get("access_token") or data.get("token")
        if not token:
            raise OsapApiError("El inicio de sesión no devolvió ningún token")
        expires_in = int(data.get("expires_in") or 3600)
        self._token = ApiToken(token, time.time() + expires_in)
        return token

    # ------------------------------------------------------------------ #
    # Operaciones
    # ------------------------------------------------------------------ #

    def list_users(self) -> list[dict]:
        """Usuarios de OSAP con sus preferencias de boletín (solo lectura)."""
        data = self._request(
            "GET", f"{self.base_url.rstrip('/')}/api/v1/admin/users",
            token=self._get_token(),
        )
        if isinstance(data, dict):
            data = data.get("items") or data.get("users") or []
        return [u for u in data if isinstance(u, dict)]

    def genres(self) -> list[dict]:
        """Catálogo de géneros musicales de osap-api."""
        data = self._request(
            "GET", f"{self.base_url.rstrip('/')}/api/v1/genres",
            token=self._get_token(),
        )
        if isinstance(data, dict):
            data = data.get("items") or []
        return data

    def search_works(self, query: str, limit: int = 5) -> list[dict]:
        qs = urllib.parse.urlencode({"q": query, "limit": limit})
        data = self._request(
            "GET", f"{self.base_url.rstrip('/')}/api/v1/search/works?{qs}",
            token=self._get_token(),
        )
        if isinstance(data, dict):
            data = data.get("items") or data.get("results") or []
        return data

    def health(self) -> dict:
        for path in ("/api/v1/system/health", "/health", "/api/v1/health"):
            try:
                return self._request("GET", f"{self.base_url.rstrip('/')}{path}")
            except OsapApiError:
                continue
        return {"status": "unreachable"}
