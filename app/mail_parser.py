"""Interpretación de un correo de petición de noticias.

El correo recibido se convierte en una :class:`NewsRequest` con:

- remitente y asunto,
- los **temas de interés** (del cuerpo, del asunto o de la cabecera ``X-Osap-Topics``),
- el **idioma** de respuesta (``código ISO`` o un nombre: *español*, *français*…),
- el número máximo de noticias y la ventana temporal.

Es un parser tolerante: acepta texto libre en español, inglés o francés, y también
un bloque ``clave: valor`` para peticiones automatizadas.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from email.message import Message
from email.utils import parseaddr

from .settings import LANGS


# --- normalización -----------------------------------------------------------

def strip_accents(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def normalize(value: str) -> str:
    return strip_accents(value).casefold().strip()


# --- idiomas -----------------------------------------------------------------

_LANG_ALIASES = {
    "es": "es", "esp": "es", "spa": "es", "spanish": "es", "espanol": "es",
    "castellano": "es", "español": "es",
    "en": "en", "eng": "en", "english": "en", "ingles": "en", "inglés": "en",
    "fr": "fr", "fra": "fr", "fre": "fr", "french": "fr", "francais": "fr", "français": "fr",
    "de": "de", "deu": "de", "ger": "de", "german": "de", "aleman": "de", "deutsch": "de",
    "it": "it", "ita": "it", "italian": "it", "italiano": "it",
    "pt": "pt", "por": "pt", "portuguese": "pt", "portugues": "pt", "português": "pt",
    "ca": "ca", "cat": "ca", "catalan": "ca", "català": "ca",
}

# Nombres de idioma reconocibles tras «en / in / auf / dans». La lista es cerrada
# a propósito: «en musicología» o «in jazz» no son peticiones de idioma.
_LANG_NAMES_RE = (
    r"(?:espa[nñ]ol|castellano|spanish|english|ingl[eé]s|fran[cç]ais|french|franc[eé]s|"
    r"deutsch|german|alem[aá]n|italiano|italian|portugu[eê]s|portuguese|catal[aà]n|catalan)"
)

# Códigos ISO-639-1: solo se aceptan tras el campo explícito («idioma: es»), nunca
# sueltos en una frase, porque «es» es también el verbo ser y artículo latino.
_LANG_CODES_RE = r"(?:es|en|fr|de|it|pt|ca)"

_LANG_PATTERNS = [
    # Campo explícito: «idioma: fr», «language = English». Admite código o nombre.
    re.compile(
        rf"\b(?:idioma|lengua|language|langue|lang)\s*[:=\-]\s*"
        rf"({_LANG_NAMES_RE}|{_LANG_CODES_RE})\b"
    ),
    # Preposición + nombre de idioma: «in English», «en español», «auf Deutsch».
    re.compile(rf"\b(?:in|en|auf|dans)\s+(?:el\s+|the\s+)?({_LANG_NAMES_RE})\b"),
]


def detect_language(text: str, default: str = "es") -> tuple[str, str]:
    """Devuelve ``(código, evidencia)``.

    Un código ISO-639-1 suelto («en») solo cuenta cuando llega como valor de un
    campo explícito, nunca dentro de una frase.
    """
    if not text:
        return default, "sin texto"
    low = normalize(text)

    if len(low) <= 3 and low in _LANG_ALIASES:
        return _LANG_ALIASES[low], "código ISO"
    for pattern in _LANG_PATTERNS:
        for match in pattern.finditer(low):
            token = match.group(1)
            code = _LANG_ALIASES.get(token)
            if code:
                return code, f"patrón «{match.group(0).strip()}»"
    # Un nombre de idioma aislado («français») sí cuenta; un código suelto no.
    for match in re.finditer(r"\b([a-zA-ZÀ-ÿ]{3,20})\b", low):
        token = match.group(1)
        if token in _LANG_ALIASES and token not in {"es", "en", "fr", "de", "it", "pt", "ca"}:
            return _LANG_ALIASES[token], f"nombre «{token}»"
    return default, "por defecto"


# --- petición ----------------------------------------------------------------

@dataclass
class NewsRequest:
    sender: str = ""
    sender_name: str = ""
    subject: str = ""
    message_id: str | None = None
    topics: list[str] = field(default_factory=list)
    language: str = "es"
    language_evidence: str = ""
    limit: int | None = None
    window_days: int | None = None
    raw_body: str = ""
    headers: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "sender": self.sender,
            "sender_name": self.sender_name,
            "subject": self.subject,
            "message_id": self.message_id,
            "topics": self.topics,
            "language": self.language,
            "language_code": LANGS.get(self.language, self.language),
            "language_evidence": self.language_evidence,
            "limit": self.limit,
            "window_days": self.window_days,
            "warnings": self.warnings,
        }


# Separadores: saltos de línea, punto y coma, barras, comas y «y / and / et».
_SPLIT = re.compile(r"[\n\r;|]+|[,]+|\s+(?:y|e|and|et|und)\s+", re.IGNORECASE)

# Una instrucción de formato («Responde en español», «5 noticias») no es un tema.
_INSTRUCTION_RE = re.compile(
    r"^(?:responde|contesta|reply|respond|send|env[ií]a|manda|please)\b",
    re.IGNORECASE,
)

# Palabras que no son temas.
_STOPWORDS = {
    "quiero", "noticias", "noticia", "news", "nouvelles", "sobre", "de", "del", "la",
    "el", "los", "las", "un", "una", "unos", "unas", "en", "por", "para", "con", "mi",
    "mis", "me", "interesa", "interesan", "interes", "interés", "temas", "tema",
    "topics", "topic", "favor", "porfa", "gracias", "hola", "buenos", "dias", "días",
    "saludos", "español", "ingles", "inglés", "frances", "francés", "idioma", "language",
    "ultimas", "últimas", "ultima", "última", "recientes", "recent", "please", "send",
    "envia", "envía", "enviar", "mandar", "manda", "suscribirme", "suscripcion",
    "suscripción", "digest", "resumen", "boletin", "boletín", "osap",
    # Conversación habitual en la petición.
    "responde", "responde", "respuesta", "contesta", "contestar", "maximo", "máximo",
    "reply", "respond", "answer", "please", "thank", "thanks", "send", "email",
    "correo", "mail", "asunto", "subject", "hola", "hello", "hi", "buenas",
    "noticias", "novedades", "news", "items", "noticia", "algunas", "algunos",
    "solo", "solamente", "puedes", "podrias", "podrías", "quiero", "quisiera",
    "necesito", "me", "gustaria", "gustaría", "informacion", "información",
}

# Fragmentos conversacionales que no deben tratarse como tema.
_NOISE_FRAGMENTS = (
    "responde", "respuesta", "contesta", "como maximo", "at most", "in english",
    "en ingles", "en espanol", "por favor",
)

# Muletillas al principio de un tema: se eliminan iterativamente y se conserva el
# resto («me interesan noticias sobre jazz» → «jazz»). Van de más a menos específico
# porque se aplican una detrás de otra.
_LEADING_FILLER = [
    re.compile(p, re.IGNORECASE) for p in (
        r"^(?:hola|buenas|hello|hi)[,.]?\s*",
        r"^(?:me interesan|me interesa)(?:\s+las)?\s+",
        r"^(?:quiero|quisiera|necesito|dame|buscame|buscar)\s+",
        r"^(?:enviame|env[ií]ame|manda|mandame)\s+",
        r"^(?:send me|i would like|i want|give me|looking for)\s+",
        r"^(?:noticias|news|informaci[oó]n|actualit[eé]s)\s+(?:sobre|de|about|sur)\s+",
        r"^(?:noticias|news|actualit[eé]s)\s+",
        r"^(?:sobre|about|sur|de|del)\s+",
        r"^(?:las|los|la|el|the)\s+",
    )
]


def parse_topics(text: str) -> list[str]:
    """Extrae la lista de temas de un texto libre."""
    if not text:
        return []
    cleaned = re.sub(r"<[^>]+>", " ", text)
    topics: list[str] = []
    seen: set[str] = set()
    # Un salto de línea o un punto separa peticiones distintas: el asunto después de
    # una coma sigue siendo parte del tema, pero «Responde en español» es otra frase.
    for raw in _SPLIT.split(cleaned):
        item = re.sub(r"^[\s\-•*·\d.)]+", "", raw).strip(" .:-\t\"'«»")
        item = re.sub(r"\s+", " ", item)
        item = item.strip(" .:-\t\"'«»")
        # «me interesan noticias sobre jazz» → «jazz» (varias pasadas hasta estabilizar).
        for _ in range(6):
            previous = item
            for pattern in _LEADING_FILLER:
                item = pattern.sub("", item)
            item = item.strip(" .:-\t\"'«»")
            if item == previous:
                break
        # Un punto seguido de espacio separa frases; el tema es la primera.
        item = re.split(r"\.\s+", item, maxsplit=1)[0].strip(" .:-\t\"'«»")
        if not item or len(item) > 120:
            continue
        low = normalize(item)
        if low in _STOPWORDS:
            continue
        if any(fragment in low for fragment in _NOISE_FRAGMENTS):
            continue
        if _INSTRUCTION_RE.search(item):
            continue
        # Una instrucción que nombra el número de noticias tampoco es un tema.
        if re.search(r"(?i)\b\d+\s+(?:noticias|news|actualités|items|results)\b", item):
            continue
        # Descarta frases conversacionales largas (>4 palabras).
        words = low.split()
        if len(words) > 4:
            continue
        if all(word in _STOPWORDS for word in words):
            continue
        key = low
        if key in seen:
            continue
        seen.add(key)
        topics.append(item)
    return topics


def _kv_fields(text: str) -> dict[str, str]:
    """Lee líneas ``clave: valor`` habituales en peticiones automatizadas."""
    fields: dict[str, str] = {}
    for line in text.splitlines():
        match = re.match(r"^\s*([A-Za-zÁÉÍÓÚÜÑáéíóúüñ_\-]{2,20})\s*:\s*(.+)$", line)
        if not match:
            continue
        fields[normalize(match.group(1)).replace("-", "_")] = match.group(2).strip()
    return fields


def _body_text(message: Message) -> str:
    if message.is_multipart():
        parts = []
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True) or b""
                parts.append(payload.decode(part.get_content_charset() or "utf-8", "replace"))
        if parts:
            return "\n".join(parts)
        for part in message.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True) or b""
                return _html_to_text(payload.decode(part.get_content_charset() or "utf-8", "replace"))
        return ""
    payload = message.get_payload(decode=True)
    if payload is None:
        # Mensaje sin codificar (8-bit): el payload ya es texto y volver a
        # decodificarlo corrompería los acentos.
        text = message.get_payload() or ""
    else:
        text = payload.decode(message.get_content_charset() or "utf-8", "replace")
    if message.get_content_type() == "text/html":
        return _html_to_text(text)
    return text


def _html_to_text(html: str) -> str:
    text = re.sub(r"(?is)<(script|style)\b.*?>.*?</\1>", " ", html)
    text = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</li>", "\n", text)
    text = re.sub(r"<[^>]+>", " ", text)
    import html as _html
    return _html.unescape(re.sub(r"[ \t]+", " ", text))


def parse_message(message: Message, default_language: str = "es") -> NewsRequest:
    """Convierte un :class:`email.message.Message` en :class:`NewsRequest`."""
    from email.header import decode_header, make_header

    raw_from = message.get("From", "") or ""
    # Con mensajes leídos en bytes, email entrega un objeto Header (no str) cuando
    # la cabecera tiene caracteres no ASCII; parseaddr fallaría y el remitente
    # quedaría vacío. Se convierte antes de analizarlo.
    if not isinstance(raw_from, str):
        try:
            raw_from = str(make_header(decode_header(str(raw_from))))
        except Exception:
            raw_from = str(raw_from)
    sender_name, sender_addr = parseaddr(raw_from)
    raw_subject = message.get("Subject") or ""
    if not isinstance(raw_subject, str):
        try:
            raw_subject = str(make_header(decode_header(str(raw_subject))))
        except Exception:
            raw_subject = str(raw_subject)

    request = NewsRequest(
        sender=sender_addr.lower(),
        sender_name=sender_name,
        subject=raw_subject.strip(),
        message_id=(message.get("Message-ID") or "").strip() or None,
        headers={k: v for k, v in message.items()},
    )
    body = _body_text(message)
    request.raw_body = body

    topics_header = message.get("X-Osap-Topics") or message.get("X-Topics")
    language_header = message.get("X-Osap-Language") or message.get("X-Language")

    fields = _kv_fields(body)
    topics_field = fields.get("temas") or fields.get("topics") or fields.get("temas_de_interes")
    language_field = fields.get("idioma") or fields.get("language") or fields.get("lang")
    limit_field = fields.get("max") or fields.get("limite") or fields.get("límite") or fields.get("limit")
    window_field = fields.get("dias") or fields.get("días") or fields.get("days") or fields.get("ventana")

    # Si el mensaje trae un campo explícito de temas se usa ese; si no, se intenta
    # primero con el asunto y, si no hay nada aprovechable, con el cuerpo completo.
    if topics_header or topics_field:
        # Se parsea solo el valor, no la línea «temas: ...» completa: si se pasara la
        # línea, «temas» se colaría como un tema más.
        request.topics = parse_topics(topics_header or topics_field)
    else:
        # Asunto y cuerpo se analizan juntos: el tema puede estar en cualquiera de
        # los dos y el parser descarta por sí solo el texto conversacional.
        request.topics = parse_topics(
            "\n".join(part for part in (request.subject, body) if part)
        )

    if not request.topics:
        request.warnings.append(
            "No se han identificado temas de interés; se devolverá la actualidad general."
        )

    # Orden de preferencia: cabecera, campo explícito del cuerpo, asunto y cuerpo.
    # Una cabecera o un campo explícito mandan sobre cualquier otra pista.
    explicit = language_header or language_field
    lang_text = explicit or "\n".join(
        part for part in (request.subject, body) if part
    )
    request.language, request.language_evidence = detect_language(lang_text, default_language)
    if explicit:
        request.language_evidence = "campo explícito"
    if request.language not in LANGS:
        request.warnings.append(f"Idioma «{request.language}» no soportado; se usará {default_language}.")
        request.language = default_language

    if limit_field:
        try:
            request.limit = max(1, min(int(re.search(r"\d+", limit_field).group()), 100))
        except (AttributeError, ValueError):
            request.warnings.append("El límite indicado no es válido; se usará el valor por defecto.")

    if window_field:
        try:
            request.window_days = max(1, min(int(re.search(r"\d+", window_field).group()), 3650))
        except (AttributeError, ValueError):
            request.warnings.append("La ventana temporal indicada no es válida.")

    return request
