"""Perfiles de usuario y sus temas de interés.

El módulo de correo funciona en dos escenarios:

- **Con perfil** (usuario ya registrado): los temas y el idioma salen del perfil.
  Lo que el correo añada se trata como refinamiento opcional de la petición.
- **Sin perfil** (usuario aún no dado de alta): los temas salen del propio correo.
  El módulo no falla ni crea perfiles de forma implícita.

El correo del usuario nunca se guarda ni se compara en claro: se calcula
``SHA-256`` del correo normalizado, que es el mismo criterio usado por
``osap-auth.users.email_lookup``.
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field

from .settings import LANGS

log = logging.getLogger(__name__)


def email_lookup(address: str) -> str:
    """Huella del correo normalizada, compatible con la de osap-auth."""
    normalized = (address or "").strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


@dataclass
class UserTopic:
    label: str
    keywords: list[str] = field(default_factory=list)
    weight: float = 1.0
    seed_code: str | None = None
    terms_by_language: dict[str, list[str]] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "label": self.label,
            "keywords": self.keywords,
            "weight": self.weight,
            "seed_code": self.seed_code,
            "terms_by_language": self.terms_by_language,
        }


@dataclass
class UserProfile:
    id: int
    email_address: str
    user_ref: str | None
    display_name: str | None
    preferred_language: str
    secondary_languages: list[str]
    max_items: int
    window_days: int
    delivery_frequency: str
    status: str
    topics: list[UserTopic] = field(default_factory=list)

    @property
    def is_active(self) -> bool:
        return self.status == "ACTIVE"

    def topics_for_language(self, language: str) -> list[UserTopic]:
        """Temas aplicables al idioma solicitado, con sus términos traducidos."""
        result = []
        for topic in self.topics:
            keywords = list(topic.keywords)
            keywords.extend(topic.terms_by_language.get(language, []))
            keywords.extend(topic.terms_by_language.get("es", []) if language != "es" else [])
            result.append(UserTopic(
                label=topic.label,
                keywords=list(dict.fromkeys(k for k in keywords if k)),
                weight=topic.weight,
                seed_code=topic.seed_code,
                terms_by_language=topic.terms_by_language,
            ))
        return result

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "user_ref": self.user_ref,
            "display_name": self.display_name,
            "preferred_language": self.preferred_language,
            "language_name": LANGS.get(self.preferred_language, self.preferred_language),
            "secondary_languages": self.secondary_languages,
            "max_items": self.max_items,
            "window_days": self.window_days,
            "delivery_frequency": self.delivery_frequency,
            "status": self.status,
            "topics": [t.as_dict() for t in self.topics],
        }


def _json_list(value) -> list:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    try:
        parsed = json.loads(value)
    except (TypeError, ValueError):
        return []
    return parsed if isinstance(parsed, list) else []


def get_profile_by_email(connection, address: str) -> UserProfile | None:
    """Devuelve el perfil activo del remitente, o ``None`` si no está registrado."""
    lookup = email_lookup(address)
    with connection.cursor() as cur:
        cur.execute(
            """SELECT id, user_ref, reply_address, display_name, preferred_language,
               secondary_languages_json, max_items, window_days, delivery_frequency, status
            FROM user_profiles WHERE email_lookup = %s""",
            (lookup,),
        )
        row = cur.fetchone()
        if not row:
            return None

        cur.execute(
            """SELECT ut.id, ut.label, ut.keywords_json, ut.weight, it.code AS seed_code
            FROM user_topics ut
            LEFT JOIN interest_topics it ON it.id = ut.interest_topic_id
            WHERE ut.profile_id = %s AND ut.active = TRUE
            ORDER BY ut.weight DESC, ut.id ASC""",
            (row["id"],),
        )
        topic_rows = cur.fetchall()

        terms: dict[int, dict[str, list[str]]] = {}
        if topic_rows:
            ids = [t["id"] for t in topic_rows]
            marks = ",".join(["%s"] * len(ids))
            cur.execute(
                f"""SELECT user_topic_id, language_code, term FROM user_topic_terms
                WHERE user_topic_id IN ({marks}) ORDER BY language_code""",
                ids,
            )
            for r in cur.fetchall():
                terms.setdefault(r["user_topic_id"], {}).setdefault(
                    r["language_code"], []
                ).append(r["term"])

    topics = [
        UserTopic(
            label=t["label"],
            keywords=_json_list(t["keywords_json"]),
            weight=float(t["weight"] or 1.0),
            seed_code=t["seed_code"],
            terms_by_language=terms.get(t["id"], {}),
        )
        for t in topic_rows
    ]
    return UserProfile(
        id=row["id"],
        email_address=row["reply_address"] or address,
        user_ref=row["user_ref"],
        display_name=row["display_name"],
        preferred_language=row["preferred_language"] or "es",
        secondary_languages=_json_list(row["secondary_languages_json"]),
        max_items=int(row["max_items"] or 20),
        window_days=int(row["window_days"] or 30),
        delivery_frequency=row["delivery_frequency"] or "ON_DEMAND",
        status=row["status"] or "ACTIVE",
        topics=topics,
    )


def create_profile(
    connection,
    address: str,
    display_name: str | None = None,
    language: str = "es",
    topics: list[str] | None = None,
    user_ref: str | None = None,
    status: str = "ACTIVE",
) -> int:
    """Crea o actualiza un perfil y sus temas a partir de etiquetas libres.

    Los temas pasan a ser del usuario: se guardan en ``user_topics`` y se enlazan
    con la semilla ``interest_topics`` cuando la etiqueta coincide con su código o nombre.
    """
    lookup = email_lookup(address)
    with connection.cursor() as cur:
        cur.execute(
            """INSERT INTO user_profiles
            (user_ref, email_lookup, reply_address, display_name, preferred_language,
             consent_at, status)
            VALUES (%s, %s, %s, %s, %s, UTC_TIMESTAMP(6), %s)
            ON DUPLICATE KEY UPDATE
              display_name = COALESCE(VALUES(display_name), display_name),
              reply_address = VALUES(reply_address),
              preferred_language = VALUES(preferred_language),
              status = VALUES(status)""",
            (user_ref, lookup, address.strip().lower(), display_name, language, status),
        )
        cur.execute("SELECT id FROM user_profiles WHERE email_lookup = %s", (lookup,))
        profile_id = int(cur.fetchone()["id"])

        cur.execute("SELECT id, code, name FROM interest_topics WHERE status='ACTIVE'")
        seed_rows = cur.fetchall()
        seeds = {row["code"].lower(): row["id"] for row in seed_rows}
        seed_names = {row["name"].lower(): row["id"] for row in seed_rows}

        for label in topics or []:
            label = (label or "").strip()
            if not label:
                continue
            seed_id = seeds.get(label.lower()) or seed_names.get(label.lower())
            cur.execute(
                """INSERT INTO user_topics (profile_id, interest_topic_id, label, weight, source)
                VALUES (%s, %s, %s, 1.00, 'USER')
                ON DUPLICATE KEY UPDATE interest_topic_id = VALUES(interest_topic_id)""",
                (profile_id, seed_id, label),
            )
    return profile_id


def set_topics(connection, profile_id: int, topics: list[str]) -> int:
    """Reemplaza los temas de un perfil."""
    with connection.cursor() as cur:
        cur.execute("DELETE FROM user_topics WHERE profile_id = %s", (profile_id,))
        cur.execute("SELECT id, code FROM interest_topics WHERE status='ACTIVE'")
        seeds = {row["code"].lower(): row["id"] for row in cur.fetchall()}
        inserted = 0
        for label in topics:
            label = (label or "").strip()
            if not label:
                continue
            cur.execute(
                """INSERT INTO user_topics (profile_id, interest_topic_id, label, weight, source)
                VALUES (%s, %s, %s, 1.00, 'USER')""",
                (profile_id, seeds.get(label.lower()), label),
            )
            inserted += 1
    return inserted


def active_profiles(connection, frequency: str | None = None) -> list[UserProfile]:
    """Perfiles activos, para el envío programado."""
    sql = "SELECT reply_address FROM user_profiles WHERE status='ACTIVE'"
    params: tuple = ()
    if frequency:
        sql += " AND delivery_frequency=%s"
        params = (frequency,)
    sql += " AND reply_address IS NOT NULL ORDER BY id"
    with connection.cursor() as cur:
        cur.execute(sql, params)
        addresses = [r["reply_address"] for r in cur.fetchall()]
    profiles = []
    for address in addresses:
        profile = get_profile_by_email(connection, address)
        if profile:
            profiles.append(profile)
    return profiles


def mark_request(connection, profile_id: int) -> None:
    with connection.cursor() as cur:
        cur.execute(
            "UPDATE user_profiles SET last_request_at=UTC_TIMESTAMP(6) WHERE id=%s",
            (profile_id,),
        )
