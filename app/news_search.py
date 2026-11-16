"""Selección de noticias por temas de interés e idioma.

Flujo:

1. Se resuelven los temas libres del correo contra los **temas semilla**
   (``interest_topics``), los **sinónimos** del catálogo OSAP (géneros, compositores,
   instrumentos) y la **taxonomía** de ``categories``.
2. Se construye una consulta SQL filtrada por idioma, estado del canal y ventana
   temporal, con las palabras clave ya resueltas.
3. Se puntúan las noticias en Python: coincidencias en título (x3), en descripción
   (x1) y en tema/editor, con bonificación por ser noticia reciente y por tipo de
   contenido. El resultado es explicable: se devuelven los términos que coinciden.

No usa IA: es determinista, auditable y barato. La IA puede añadirse después como
reordenador, sin cambiar este módulo.
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from .mail_parser import normalize
from .osap_catalog import OsapVocabulary

log = logging.getLogger(__name__)

MAX_CANDIDATES = 800

# El corpus incluye fuentes generalistas (agenda cultural, repositorios académicos,
# textos de Wikisource). Una noticia debe mencionar vocabulario musical para que
# una coincidencia sea relevante: sin este filtro, «patrimonio» casa con un cuento
# y «research» con estudios de medicina.
# Términos que, sin más contexto, producen falsos positivos en textos no musicales:
# «organ» aparece en prensa orgánica y «organizar»; «score» en resultados deportivos.
AMBIGUOUS_TERMS = {
    "organ", "organo", "score", "band", "play", "playing", "tone", "note",
    "piece", "number", "record", "air", "solo", "concertar", "sinfonia",
}

MUSIC_MARKERS = (
    "música", "musical", "musico", "compositor", "compositora", "composición",
    "concierto", "orquesta", "ópera", "partitura", "cantante", "intérprete",
    "instrumento", "piano", "violín", "violonchelo", "guitarra", "flauta",
    "trompeta", "saxofón", "batería", "coro", "coral", "director de orquesta",
    "music", "musical", "musician", "composer", "composition", "concert",
    "orchestra", "symphony", "opera", "score", "sheet music", "singer",
    "performer", "instrument", "piano", "violin", "cello", "guitar", "flute",
    "trumpet", "saxophone", "drums", "choir", "choral", "conductor", "album",
    "band", "song", "songwriter", "musique", "musicien", "compositeur",
    "orchestre", "opéra", "partition", "chanteur", "instrument", "violon",
    "guitare", "chœur", "chef d'orchestre", "disque",
)


def _is_music_related(title: str, body: str) -> bool:
    """Comprueba que el texto hable de música como palabra completa.

    Se usa límite de palabra a ambos lados: si no, «opera» casaría con «operate»
    y «musical» con «musicality» en contextos ajenos a la música.
    """
    haystack = f"{title} {body}"
    for marker in MUSIC_MARKERS:
        if " " in marker:
            if marker in haystack:
                return True
        elif re.search(rf"\b{re.escape(marker)}\b", haystack):
            return True
    return False


@dataclass
class TopicResolution:
    """Resultado de expandir un tema escrito por el usuario."""

    query: str
    matched_topic: str | None = None
    keywords: list[str] = field(default_factory=list)
    genres: list[str] = field(default_factory=list)
    category_codes: list[str] = field(default_factory=list)
    osap_terms: list[str] = field(default_factory=list)
    weight: float = 1.0

    def as_dict(self) -> dict:
        return {
            "query": self.query,
            "matched_topic": self.matched_topic,
            "keywords": self.keywords,
            "genres": self.genres,
            "category_codes": self.category_codes,
            "osap_terms": self.osap_terms,
            "weight": self.weight,
        }

    @property
    def is_empty(self) -> bool:
        return not (self.keywords or self.genres or self.osap_terms)


@dataclass
class NewsHit:
    news_item_id: int
    publication_id: int | None
    title: str
    summary: str
    url: str | None
    published_at: datetime | None
    publisher: str | None
    channel: str | None
    language: str
    content_type: str | None
    score: float
    matched: list[str]

    def as_dict(self) -> dict:
        return {
            "news_item_id": self.news_item_id,
            "publication_id": self.publication_id,
            "title": self.title,
            "summary": self.summary,
            "url": self.url,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "publisher": self.publisher,
            "channel": self.channel,
            "language": self.language,
            "content_type": self.content_type,
            "score": round(self.score, 3),
            "matched": self.matched,
        }


def _clean_text(value: str | None) -> str:
    """Quita HTML y entidades de un texto de feed."""
    if not value:
        return ""
    import html

    text = html.unescape(value)
    text = re.sub(r"(?is)<(script|style)\b.*?>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<[^>]*>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def load_seed_topics(connection) -> list[dict]:
    with connection.cursor() as cur:
        cur.execute(
            """SELECT code, name, description, keywords_json, osap_genre_ids_json,
               category_codes_json FROM interest_topics WHERE status='ACTIVE' ORDER BY id"""
        )
        rows = cur.fetchall()
        # Términos por idioma de cada tema semilla (migración 010).
        cur.execute(
            """SELECT t.code, tt.language_code, tt.term
            FROM interest_topic_terms tt
            JOIN interest_topics t ON t.id = tt.interest_topic_id"""
        )
        term_rows = cur.fetchall()

    terms_by_topic: dict[str, dict[str, list[str]]] = {}
    for row in term_rows:
        terms_by_topic.setdefault(row["code"], {}).setdefault(
            row["language_code"], []
        ).append(row["term"])

    topics = []
    for row in rows:
        def _load(value):
            if value is None:
                return []
            if isinstance(value, (list, tuple)):
                return list(value)
            try:
                return json.loads(value)
            except (TypeError, ValueError):
                return []
        topics.append({
            "code": row["code"],
            "name": row["name"],
            "description": row["description"] or "",
            "keywords": _load(row["keywords_json"]),
            "genres": _load(row["osap_genre_ids_json"]),
            "categories": _load(row["category_codes_json"]),
            "terms_by_language": terms_by_topic.get(row["code"], {}),
        })
    return topics


def load_category_names(connection, codes: list[str]) -> list[str]:
    if not codes:
        return []
    marks = ",".join(["%s"] * len(codes))
    with connection.cursor() as cur:
        cur.execute(f"SELECT code, name FROM categories WHERE code IN ({marks})", codes)
        return [f"{r['name']}" for r in cur.fetchall()]


def resolve_topic(
    query: str,
    seeds: list[dict],
    vocabulary: OsapVocabulary,
    category_names: dict[str, str] | None = None,
    language: str = "es",
) -> TopicResolution:
    """Expande un tema libre contra la semilla, la taxonomía y el catálogo OSAP."""
    resolution = TopicResolution(query=query)
    norm_query = normalize(query)
    if not norm_query:
        return resolution

    # 1) Tema semilla: coincidencia exacta, por contención o por palabra clave.
    #    Las variantes incluyen singular y plural (p. ej. «Orchestras» → «orchestra»).
    query_variants = {norm_query, *_term_variants(norm_query)}
    for seed in seeds:
        names = [normalize(seed["code"]), normalize(seed["name"])]
        keys = [normalize(k) for k in seed["keywords"]]
        localized_raw = list(seed.get("terms_by_language", {}).get(language, []))
        localized = [normalize(k) for k in localized_raw]
        candidates = names + keys + localized
        candidate_variants: set[str] = set()
        for candidate in candidates:
            candidate_variants.update(_term_variants(candidate))
        if (
            any(q in names for q in query_variants)
            or any(n and n in norm_query for n in names if len(n) > 4)
            or any(k and k in query_variants for k in candidates)
            or any(k in norm_query or norm_query in k for k in candidates if len(k) > 4)
            or bool(query_variants & candidate_variants)
        ):
            resolution.matched_topic = seed["code"]
            resolution.keywords = list(dict.fromkeys([seed["name"], *seed["keywords"]]))
            resolution.genres = [vocabulary.genres.get(int(g), "") for g in seed["genres"]]
            resolution.genres = [g for g in resolution.genres if g]
            resolution.category_codes = list(seed["categories"])
            # Términos en el idioma de respuesta: sin esto, un tema en inglés no
            # encontraría noticias inglesas escritas con otras palabras.
            resolution.keywords.extend(localized_raw)
            # Se añaden también los términos de los otros idiomas del tema: una noticia
            # inglesa puede citar «ópera» o «opéra» y debe encontrarse igual.
            for other_lang, terms in seed.get("terms_by_language", {}).items():
                if other_lang != language:
                    resolution.keywords.extend(terms)
            break

    if not resolution.matched_topic:
        resolution.keywords = [query]

    # 2) Taxonomía: nombres de categoría que contengan el tema.
    if category_names:
        extra = [
            name for name in category_names.values()
            if norm_query and (norm_query in normalize(name) or normalize(name) in norm_query)
        ]
        resolution.keywords.extend(extra)

    # 3) Catálogo OSAP (vía API): géneros que casan con el tema.
    if vocabulary.available:
        for name in vocabulary.genres.values():
            n = normalize(name)
            if n and (norm_query in n or n in norm_query):
                resolution.genres.append(name)

    resolution.keywords = list(dict.fromkeys(k for k in resolution.keywords if k))
    resolution.genres = list(dict.fromkeys(resolution.genres))
    resolution.osap_terms = list(dict.fromkeys(resolution.osap_terms))
    return resolution


def _like_terms(resolutions: list[TopicResolution]) -> list[str]:
    """Términos para el LIKE del SQL, con variantes de plural.

    Se usa la raíz más corta (4 caracteres mínimo) para que «orchestras» y
    «orchestra» caigan en la misma consulta; el puntuado posterior descarta
    coincidencias parciales arbitrarias.
    """
    terms: list[str] = []
    for res in resolutions:
        for term in (res.keywords + res.genres + res.osap_terms):
            term = term.strip()
            if len(term) < 3:
                continue
            variant = term
            low = normalize(term)
            if len(low) > 6 and low.endswith("s"):
                variant = term[:-1]
            terms.append(variant)
    return list(dict.fromkeys(terms))[:60]


def search_news(
    connection,
    resolutions: list[TopicResolution],
    language: str,
    limit: int = 20,
    window_days: int = 30,
    now: datetime | None = None,
) -> list[NewsHit]:
    """Devuelve las noticias más relevantes para los temas resueltos e idioma."""
    now = now or datetime.now(timezone.utc).replace(tzinfo=None)
    since = now - timedelta(days=window_days)
    terms = _like_terms(resolutions)
    # Fecha efectiva: la de publicación y, si la fuente no la trae, la de captura.
    # Los feeds sin fecha (Internet Archive, BnF) se evalúan por cuándo se vieron.
    date_expr = "COALESCE(p.published_at, p.first_seen_at)"

    where_terms = ""
    params: list = [language, since, now]
    if terms:
        clauses = []
        for term in terms:
            clauses.append("(p.title_original LIKE %s OR p.description_original LIKE %s)")
            like = f"%{term}%"
            params.extend([like, like])
        where_terms = " AND (" + " OR ".join(clauses) + ")"

    sql = f"""
        SELECT p.id AS publication_id, p.news_item_id, p.title_original,
               p.description_original, p.canonical_url, p.published_at,
               p.language_declared, pv.name AS publisher, s.name AS channel,
               COALESCE(p.language_detected, s.declared_language) AS language,
               ct.code AS content_type
        FROM news_publications p
        JOIN news_items n ON n.id = p.news_item_id AND n.status = 'ACTIVE'
        LEFT JOIN publishers pv ON pv.id = p.publisher_id
        LEFT JOIN source_observations o ON o.news_publication_id = p.id
        LEFT JOIN source_channels s ON s.id = o.source_channel_id
        LEFT JOIN content_types ct ON ct.id = s.default_content_type_id
        WHERE COALESCE(p.language_detected, s.declared_language, 'es') = %s
          AND s.status = 'ACTIVE'
          AND s.delivery_mode <> 'MANUAL'
          AND {date_expr} >= %s
          AND {date_expr} <= %s
          {where_terms}
        ORDER BY {date_expr} DESC
        LIMIT {MAX_CANDIDATES}
    """
    # El idioma se compara también con el declarado por canal cuando no hay detectado.
    params[0] = language
    try:
        with connection.cursor() as cur:
            cur.execute(sql, tuple(params))
            rows = cur.fetchall()
    except Exception as exc:  # pragma: no cover
        log.error("Error en la consulta de noticias: %s", exc)
        return []

    if not rows and not terms:
        # Sin temas en el corpus: se devuelve lo más reciente.
        return _latest(connection, language, limit, since, now)

    return _rank(rows, resolutions, limit, now)


def _latest(connection, language: str, limit: int, since, now) -> list[NewsHit]:
    with connection.cursor() as cur:
        cur.execute(
            """SELECT p.id AS publication_id, p.news_item_id, p.title_original,
               p.description_original, p.canonical_url, p.published_at,
               pv.name AS publisher, s.name AS channel,
               COALESCE(p.language_detected, s.declared_language) AS language,
               ct.code AS content_type
            FROM news_publications p
            JOIN news_items n ON n.id = p.news_item_id AND n.status='ACTIVE'
            LEFT JOIN publishers pv ON pv.id=p.publisher_id
            LEFT JOIN source_observations o ON o.news_publication_id=p.id
            LEFT JOIN source_channels s ON s.id=o.source_channel_id
            LEFT JOIN content_types ct ON ct.id=s.default_content_type_id
            WHERE COALESCE(p.language_detected, s.declared_language, 'es')=%s
              AND s.status='ACTIVE' AND s.delivery_mode <> 'MANUAL'
              AND COALESCE(p.published_at, p.first_seen_at) BETWEEN %s AND %s
            ORDER BY COALESCE(p.published_at, p.first_seen_at) DESC
            LIMIT %s""",
            (language, since, now, limit),
        )
        rows = cur.fetchall()
    return [_hit_from_row(r, 0.0, []) for r in rows]


def _hit_from_row(row: dict, score: float, matched: list[str]) -> NewsHit:
    summary = _clean_text(row["description_original"])
    return NewsHit(
        news_item_id=row["news_item_id"],
        publication_id=row["publication_id"],
        title=_clean_text(row["title_original"]),
        summary=summary,
        url=row["canonical_url"],
        published_at=row["published_at"],
        publisher=row["publisher"],
        channel=row["channel"],
        language=row["language"] or "",
        content_type=row["content_type"],
        score=score,
        matched=matched,
    )


def _term_variants(term: str) -> list[str]:
    """Variantes morfológicas simples del término (plurales en/es/fr).

    Evita que «Orchestras» no encuentre «orchestra» o que «conciertos» no
    encuentre «concierto».
    """
    base = normalize(term)
    if not base:
        return []
    variants = {base}
    if len(base) > 4:
        if base.endswith("ies"):
            variants.add(base[:-3] + "y")
        if base.endswith("es") and len(base) > 5:
            variants.add(base[:-2])
        if base.endswith("s"):
            variants.add(base[:-1])
        if base.endswith("es"):
            variants.add(base[:-1])
        # Singular → plural, por si el término viene en singular.
        variants.add(base + "s")
    # Raíz con comodín controlado para plurales irregulares (jazz, blues…).
    if len(base) >= 4 and not base.endswith("*"):
        variants.add(base + "*")
    return sorted(v for v in variants if len(v.rstrip("*")) >= 3)


def _rank(rows: list[dict], resolutions: list[TopicResolution], limit: int,
          now: datetime) -> list[NewsHit]:
    hits: dict[int, NewsHit] = {}
    # Los historiales de Wikipedia («Pac Veten: CE - grammar…») son ruido editorial:
    # coinciden por acumulación de texto y nunca son noticias útiles.
    rows = [r for r in rows if (r.get("content_type") or "") != "OTHER"]
    for row in rows:
        title = normalize(_clean_text(row["title_original"]))
        body = normalize(_clean_text(row["description_original"]))
        score = 0.0
        matched: list[str] = []
        for res in resolutions:
            for term in res.keywords + res.genres + res.osap_terms:
                best = 0.0
                # Los términos ambiguos exigen contexto musical explícito: se
                # evalúan como palabra completa y sin derivar plurales.
                if normalize(term) in AMBIGUOUS_TERMS:
                    if re.search(rf"\b{re.escape(normalize(term))}\b", title):
                        best = max(best, 1.0)
                    continue
                for variant in _term_variants(term):
                    if variant.endswith("*"):
                        # Raíz explícita (plurales): se permite cualquier sufijo.
                        pattern = re.compile(rf"\b{re.escape(variant[:-1])}\w*")
                    else:
                        # Siempre palabra completa: «opera» no debe casar con
                        # «operating» ni «partitura» con «partituras» mal cortadas.
                        pattern = re.compile(rf"\b{re.escape(variant)}\b")
                    if pattern.search(title):
                        best = max(best, 3.0)
                    elif pattern.search(body):
                        best = max(best, 1.0)
                if best:
                    score += best * res.weight
                    matched.append(term)
        if score <= 0:
            continue
        if not _is_music_related(title, body):
            continue
        published = row["published_at"]
        if published:
            age_days = (now - published).days
            score += max(0.0, 2.0 - age_days / 30.0)
            # Refuerzo por proximidad temporal: lo de este mes pesa más que lo de hace
            # un año, que en feeds de archivo también aparece «vigente».
            if age_days <= 31:
                score += 1.0
            elif age_days > 366:
                score -= 1.0
        if row["content_type"] in {"EVENT", "NEWS"}:
            score += 0.5
        matched = list(dict.fromkeys(matched))[:8]
        hit = _hit_from_row(row, score, matched)
        existing = hits.get(hit.news_item_id)
        if existing is None or hit.score > existing.score:
            hits[hit.news_item_id] = hit

    ranked = sorted(
        hits.values(),
        key=lambda h: (h.score, h.published_at or datetime.min),
        reverse=True,
    )
    return ranked[:limit]
