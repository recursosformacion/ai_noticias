"""Composición del correo de respuesta con la lista de noticias.

Genera un mensaje ``multipart/alternative`` con versión en texto plano y en HTML.
Todos los textos de la plantilla existen en es, en, fr, de, it, pt y ca; si falta
un idioma se usa el español.
"""
from __future__ import annotations

from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from html import escape

from .news_search import NewsHit

TEXTS = {
    "es": {
        "subject": "Tus noticias musicales: {topics}",
        "subject_empty": "Tus noticias musicales",
        "greeting": "Hola{name},",
        "intro": "Estas son las noticias musicales más relevantes para tus temas de interés.",
        "intro_profile": "Estas son las noticias musicales que coinciden con los temas de tu perfil.",
        "topics": "Temas consultados",
        "language": "Idioma",
        "none": "No hemos encontrado noticias que coincidan con tus temas en el periodo consultado.",
        "none_hint": "Prueba a ampliar la ventana temporal o a matizar los temas.",
        "source": "Fuente",
        "date": "Fecha",
        "matched": "Coincide con",
        "footer": "Este correo lo genera automáticamente el servicio de noticias de OSAP a partir de fuentes de libre difusión.",
        "footer_rights": "Los contenidos pertenecen a sus editores; consulta el enlace original para la atribución completa.",
        "count": "{n} noticias",
        "read_more": "Leer la noticia",
        "warnings": "Notas sobre tu petición",
    },
    "en": {
        "subject": "Your music news: {topics}",
        "subject_empty": "Your music news",
        "greeting": "Hello{name},",
        "intro": "Here are the music news items most relevant to your interests.",
        "intro_profile": "Here are the music news items matching the topics in your profile.",
        "topics": "Requested topics",
        "language": "Language",
        "none": "We found no news matching your topics in the requested period.",
        "none_hint": "Try widening the time window or refining the topics.",
        "source": "Source",
        "date": "Date",
        "matched": "Matches",
        "footer": "This email is generated automatically by the OSAP news service from openly licensed sources.",
        "footer_rights": "Content belongs to its publishers; see the original link for full attribution.",
        "count": "{n} news items",
        "read_more": "Read the news",
        "warnings": "Notes about your request",
    },
    "fr": {
        "subject": "Vos actualités musicales : {topics}",
        "subject_empty": "Vos actualités musicales",
        "greeting": "Bonjour{name},",
        "intro": "Voici les actualités musicales les plus pertinentes pour vos centres d'intérêt.",
        "intro_profile": "Voici les actualités musicales correspondant aux thèmes de votre profil.",
        "topics": "Thèmes demandés",
        "language": "Langue",
        "none": "Aucune actualité ne correspond à vos thèmes sur la période demandée.",
        "none_hint": "Essayez d'élargir la période ou de préciser les thèmes.",
        "source": "Source",
        "date": "Date",
        "matched": "Correspond à",
        "footer": "Cet e-mail est généré automatiquement par le service d'actualités OSAP à partir de sources librement diffusées.",
        "footer_rights": "Les contenus appartiennent à leurs éditeurs ; consultez le lien original pour l'attribution.",
        "count": "{n} actualités",
        "read_more": "Lire l'actualité",
        "warnings": "Remarques sur votre demande",
    },
    "de": {
        "subject": "Deine Musiknachrichten: {topics}",
        "subject_empty": "Deine Musiknachrichten",
        "greeting": "Hallo{name},",
        "intro": "Hier sind die relevantesten Musiknachrichten zu deinen Interessen.",
        "intro_profile": "Hier sind die Musiknachrichten, die zu den Themen deines Profils passen.",
        "topics": "Angefragte Themen",
        "language": "Sprache",
        "none": "Im gewählten Zeitraum wurden keine passenden Nachrichten gefunden.",
        "none_hint": "Erweitere den Zeitraum oder präzisiere die Themen.",
        "source": "Quelle",
        "date": "Datum",
        "matched": "Passt zu",
        "footer": "Diese E-Mail wird automatisch vom OSAP-Nachrichtendienst aus frei lizenzierten Quellen erzeugt.",
        "footer_rights": "Die Inhalte gehören den Herausgebern; beachte den Originallink.",
        "count": "{n} Nachrichten",
        "read_more": "Zur Nachricht",
        "warnings": "Hinweise zu deiner Anfrage",
    },
    "it": {
        "subject": "Le tue notizie musicali: {topics}",
        "subject_empty": "Le tue notizie musicali",
        "greeting": "Ciao{name},",
        "intro": "Ecco le notizie musicali più rilevanti per i tuoi interessi.",
        "intro_profile": "Ecco le notizie musicali che corrispondono ai temi del tuo profilo.",
        "topics": "Temi richiesti",
        "language": "Lingua",
        "none": "Nessuna notizia corrisponde ai tuoi temi nel periodo richiesto.",
        "none_hint": "Prova ad ampliare il periodo o a precisare i temi.",
        "source": "Fonte",
        "date": "Data",
        "matched": "Corrisponde a",
        "footer": "Questa email è generata automaticamente dal servizio notizie OSAP da fonti liberamente diffuse.",
        "footer_rights": "I contenuti appartengono ai loro editori; consulta il link originale.",
        "count": "{n} notizie",
        "read_more": "Leggi la notizia",
        "warnings": "Note sulla tua richiesta",
    },
    "pt": {
        "subject": "As suas notícias musicais: {topics}",
        "subject_empty": "As suas notícias musicais",
        "greeting": "Olá{name},",
        "intro": "Estas são as notícias musicais mais relevantes para os seus interesses.",
        "intro_profile": "Estas são as notícias musicais que correspondem aos temas do seu perfil.",
        "topics": "Temas pedidos",
        "language": "Idioma",
        "none": "Não encontrámos notícias que correspondam aos seus temas no período pedido.",
        "none_hint": "Tente alargar o período ou precisar os temas.",
        "source": "Fonte",
        "date": "Data",
        "matched": "Corresponde a",
        "footer": "Este email é gerado automaticamente pelo serviço de notícias OSAP a partir de fontes de livre difusão.",
        "footer_rights": "Os conteúdos pertencem aos seus editores; consulte a ligação original.",
        "count": "{n} notícias",
        "read_more": "Ler a notícia",
        "warnings": "Notas sobre o seu pedido",
    },
    "ca": {
        "subject": "Les teves notícies musicals: {topics}",
        "subject_empty": "Les teves notícies musicals",
        "greeting": "Hola{name},",
        "intro": "Aquestes són les notícies musicals més rellevants per als teus interessos.",
        "intro_profile": "Aquestes són les notícies musicals que coincideixen amb els temes del teu perfil.",
        "topics": "Temes consultats",
        "language": "Idioma",
        "none": "No hem trobat notícies que coincideixin amb els teus temes en el període consultat.",
        "none_hint": "Prova d'ampliar la finestra temporal o de matisar els temes.",
        "source": "Font",
        "date": "Data",
        "matched": "Coincideix amb",
        "footer": "Aquest correu el genera automàticament el servei de notícies de l'OSAP a partir de fonts de lliure difusió.",
        "footer_rights": "Els continguts pertanyen als seus editors; consulta l'enllaç original.",
        "count": "{n} notícies",
        "read_more": "Llegeix la notícia",
        "warnings": "Notes sobre la teva petició",
    },
}


def texts_for(language: str) -> dict:
    return TEXTS.get(language, TEXTS["es"])


def _date_label(value: datetime | None, language: str) -> str:
    if not value:
        return ""
    fmt = "%d/%m/%Y" if language in {"es", "fr", "pt", "ca", "it"} else "%Y-%m-%d"
    return value.strftime(fmt)


def _summary(hit: NewsHit, limit: int = 320) -> str:
    text = (hit.summary or "").strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut + "…"


def build_subject(topics: list[str], language: str) -> str:
    t = texts_for(language)
    if not topics:
        return t["subject_empty"]
    label = ", ".join(topics[:3])
    if len(topics) > 3:
        label += "…"
    return t["subject"].format(topics=label)


def build_text_body(
    hits: list[NewsHit],
    topics: list[str],
    language: str,
    warnings: list[str] | None = None,
    recipient_name: str | None = None,
    from_profile: bool = False,
) -> str:
    t = texts_for(language)
    lines = [
        t["greeting"].format(name=f" {recipient_name}" if recipient_name else ""),
        "",
        t["intro_profile"] if from_profile else t["intro"],
        "",
        f"{t['topics']}: {', '.join(topics) if topics else '—'}",
        f"{t['language']}: {language}",
        "",
        "=" * 70,
        "",
    ]
    if not hits:
        lines.extend([t["none"], t["none_hint"], ""])
    for i, hit in enumerate(hits, start=1):
        lines.append(f"{i}. {hit.title}")
        meta = []
        if hit.publisher:
            meta.append(hit.publisher)
        if hit.published_at:
            meta.append(_date_label(hit.published_at, language))
        if hit.content_type:
            meta.append(hit.content_type)
        if meta:
            lines.append("   " + " · ".join(meta))
        summary = _summary(hit)
        if summary:
            lines.append(f"   {summary}")
        if hit.url:
            lines.append(f"   {t['read_more']}: {hit.url}")
        if hit.matched:
            lines.append(f"   {t['matched']}: {', '.join(hit.matched[:5])}")
        lines.append("")
    lines.append("=" * 70)
    if warnings:
        lines.append(f"{t['warnings']}:")
        for warning in warnings:
            lines.append(f"  - {warning}")
        lines.append("")
    lines.append(t["footer"])
    lines.append(t["footer_rights"])
    return "\n".join(lines)


def build_html_body(
    hits: list[NewsHit],
    topics: list[str],
    language: str,
    warnings: list[str] | None = None,
    recipient_name: str | None = None,
    from_profile: bool = False,
) -> str:
    t = texts_for(language)
    greeting = escape(t["greeting"].format(name=f" {recipient_name}" if recipient_name else ""))
    intro = escape(t["intro_profile"] if from_profile else t["intro"])

    items_html = []
    for hit in hits:
        meta_parts = []
        if hit.publisher:
            meta_parts.append(escape(hit.publisher))
        if hit.published_at:
            meta_parts.append(_date_label(hit.published_at, language))
        if hit.content_type:
            meta_parts.append(escape(hit.content_type))
        meta = " · ".join(meta_parts)
        title = escape(hit.title)
        link = f'<a href="{escape(hit.url)}" style="color:#1f4e79;text-decoration:none">{title}</a>' if hit.url else title
        matched = ""
        if hit.matched:
            matched = (
                f'<p style="margin:4px 0 0;font-size:12px;color:#777">'
                f'{escape(t["matched"])}: {escape(", ".join(hit.matched[:5]))}</p>'
            )
        summary = escape(_summary(hit))
        items_html.append(
            f'<div style="border-left:3px solid #1f4e79;padding:10px 14px;margin:0 0 16px">'
            f'<p style="margin:0 0 4px;font-size:16px;font-weight:600">{link}</p>'
            f'<p style="margin:0 0 6px;font-size:12px;color:#555">{meta}</p>'
            f'<p style="margin:0;font-size:13px;line-height:1.5">{summary}</p>'
            f'{matched}</div>'
        )

    empty_html = ""
    if not hits:
        empty_html = (
            f'<p style="padding:16px;background:#f5f5f5;border-radius:6px">{escape(t["none"])}<br>'
            f'<span style="color:#666;font-size:13px">{escape(t["none_hint"])}</span></p>'
        )

    warnings_html = ""
    if warnings:
        lis = "".join(f"<li>{escape(w)}</li>" for w in warnings)
        warnings_html = (
            f'<div style="margin:20px 0;padding:10px 14px;background:#fff8e1;border-radius:6px">'
            f'<p style="margin:0 0 6px;font-weight:600;font-size:13px">{escape(t["warnings"])}</p>'
            f'<ul style="margin:0;padding-left:18px;font-size:13px">{lis}</ul></div>'
        )

    topics_label = escape(", ".join(topics) if topics else "—")
    count_label = escape(t["count"].format(n=len(hits)))

    return f"""<!DOCTYPE html>
<html lang="{escape(language)}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f0f0f0;font-family:Segoe UI,Helvetica,Arial,sans-serif;color:#222">
<div style="max-width:680px;margin:0 auto;background:#fff">
  <div style="background:#1f4e79;color:#fff;padding:22px 26px">
    <p style="margin:0;font-size:20px;font-weight:600">OSAP · Noticias musicales</p>
    <p style="margin:6px 0 0;font-size:13px;opacity:.85">{count_label}</p>
  </div>
  <div style="padding:22px 26px">
    <p style="margin:0 0 10px;font-size:15px">{greeting}</p>
    <p style="margin:0 0 16px;font-size:14px;line-height:1.5">{intro}</p>
    <p style="margin:0 0 4px;font-size:13px;color:#555"><strong>{escape(t["topics"])}:</strong> {topics_label}</p>
    <p style="margin:0 0 20px;font-size:13px;color:#555"><strong>{escape(t["language"])}:</strong> {escape(language)}</p>
    {empty_html}
    {''.join(items_html)}
    {warnings_html}
  </div>
  <div style="padding:16px 26px;background:#f7f7f7;font-size:11px;color:#777;line-height:1.5">
    <p style="margin:0 0 4px">{escape(t["footer"])}</p>
    <p style="margin:0">{escape(t["footer_rights"])}</p>
  </div>
</div>
</body></html>"""


def build_reply(
    to_address: str,
    hits: list[NewsHit],
    topics: list[str],
    language: str,
    from_address: str = "noticias@osap.local",
    from_name: str = "OSAP Noticias",
    reply_to: str | None = None,
    subject: str | None = None,
    in_reply_to: str | None = None,
    references: str | None = None,
    warnings: list[str] | None = None,
    recipient_name: str | None = None,
    from_profile: bool = False,
) -> EmailMessage:
    """Construye el mensaje de respuesta listo para enviar."""
    message = EmailMessage()
    message["From"] = formataddr((from_name, from_address))
    message["To"] = to_address
    if reply_to:
        message["Reply-To"] = reply_to
    message["Subject"] = subject or build_subject(topics, language)
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain=from_address.split("@")[-1] or "osap.local")
    if in_reply_to:
        message["In-Reply-To"] = in_reply_to
        message["References"] = references or in_reply_to
    message["X-Osap-Language"] = language
    message["X-Osap-Topic-Source"] = "PROFILE" if from_profile else "EMAIL"
    message["X-Osap-Items"] = str(len(hits))
    message["Auto-Submitted"] = "auto-replied"

    message.set_content(
        build_text_body(hits, topics, language, warnings, recipient_name, from_profile)
    )
    message.add_alternative(
        build_html_body(hits, topics, language, warnings, recipient_name, from_profile),
        subtype="html",
    )
    return message


def build_error_reply(
    to_address: str,
    error_text: str,
    language: str = "es",
    from_address: str = "noticias@osap.local",
    from_name: str = "OSAP Noticias",
    in_reply_to: str | None = None,
) -> EmailMessage:
    message = EmailMessage()
    message["From"] = formataddr((from_name, from_address))
    message["To"] = to_address
    message["Subject"] = texts_for(language)["subject_empty"]
    message["Date"] = formatdate(localtime=True)
    message["Message-ID"] = make_msgid(domain=from_address.split("@")[-1] or "osap.local")
    if in_reply_to:
        message["In-Reply-To"] = in_reply_to
    message["Auto-Submitted"] = "auto-replied"
    message.set_content(error_text)
    return message
