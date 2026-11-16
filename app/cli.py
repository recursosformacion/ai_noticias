"""Comandos locales para la captura de noticias."""
from __future__ import annotations

import argparse
import json
import os
import sys

from .analyzer import NewsAnalyzer
from .collector import ingest_active_channels, probe_candidate_channels
from .db import connect


def main() -> int:
    parser = argparse.ArgumentParser(prog="ai-noticias")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("sources", help="Mostrar los canales registrados y su estado.")

    probe = sub.add_parser(
        "probe", help="Comprobar LOC y BnF sin guardar elementos ni modificar la base."
    )
    probe.add_argument("--source-id", type=int, help="Limitar la prueba a un canal permitido.")

    ingest = sub.add_parser("ingest", help="Consultar fuentes RSS/Atom activas.")
    ingest.add_argument("--source-id", type=int, help="Limitar la ejecución a un canal.")

    activate = sub.add_parser("activate", help="Activar un canal tras revisar sus condiciones.")
    activate.add_argument("--source-id", type=int, required=True)
    activate.add_argument(
        "--confirm-terms-reviewed", action="store_true",
        help="Confirma que se han revisado los términos y el uso previsto."
    )

    analyze = sub.add_parser("analyze", help="Analizar noticias capturadas con IA.")
    analyze.add_argument("--limit", type=int, default=10, help="Límite de noticias a analizar.")

    # --- módulo de noticias por correo ---
    mail = sub.add_parser("mail", help="Responder a un correo con noticias por temas e idioma.")
    mail.add_argument("--eml", help="Fichero .eml con el correo recibido.")
    mail.add_argument("--from", dest="sender", help="Remitente (si no se usa --eml).")
    mail.add_argument("--topics", help="Temas separados por comas (si no se usa --eml).")
    mail.add_argument("--lang", default="es", help="Idioma de respuesta: es, en, fr, de, it, pt, ca.")
    mail.add_argument("--limit", type=int, help="Número máximo de noticias.")
    mail.add_argument("--days", type=int, help="Ventana temporal en días.")
    mail.add_argument(
        "--queue", choices=["QUEUE", "FILE", "NONE"], default="NONE",
        help="Entrega: QUEUE (la envía OSAP), FILE (.eml en disco) o NONE.",
    )
    mail.add_argument("--save", help="Guardar la respuesta como .eml.")

    mailbox = sub.add_parser(
        "mailbox", help="Procesar los correos recibidos (carpeta .eml o entrada estándar)."
    )
    mailbox.add_argument("--dir", help="Carpeta con ficheros .eml a procesar.")
    mailbox.add_argument("--stdin", action="store_true", help="Leer un mensaje de la entrada estándar.")
    mailbox.add_argument("--delivery", choices=["QUEUE", "FILE", "NONE"],
                         help="Destino de la respuesta (por defecto, el de osap.toml).")

    # --- proceso periódico (cron): capturar y enviar a los suscriptores ---
    digest = sub.add_parser(
        "digest", help="Ciclo completo: actualizar noticias y enviar el boletín a los suscriptores."
    )
    digest.add_argument("--no-ingest", action="store_true",
                        help="No capturar fuentes; usar solo lo ya almacenado.")
    digest.add_argument("--delivery", choices=["QUEUE", "FILE", "NONE"],
                        help="Destino de los boletines (por defecto, el de osap.toml).")
    digest.add_argument("--days", type=int, help="Ventana temporal en días.")
    digest.add_argument("--user", help="Procesar solo el usuario con este user_ref.")
    digest.add_argument("--dry-run", action="store_true",
                        help="Calcular sin escribir en la cola.")
    digest.add_argument("--to", help="Enviar a una dirección concreta (prueba manual).")
    digest.add_argument("--all-topics", action="store_true",
                        help="Usar todos los temas, ignorando los del usuario.")
    digest.add_argument("--lang", help="Idioma para el envío de prueba con --to.")

    sub.add_parser("mail-check", help="Comprobar configuración del módulo y catálogo OSAP.")

    profile = sub.add_parser("profile", help="Alta y consulta de perfiles de usuario.")
    profile.add_argument("--email", required=True, help="Correo del usuario.")
    profile.add_argument("--name", help="Nombre visible.")
    profile.add_argument("--topics", help="Temas de interés separados por comas.")
    profile.add_argument("--lang", default="es", help="Idioma preferido.")
    profile.add_argument("--show", action="store_true", help="Solo consultar el perfil.")

    args = parser.parse_args()
    connection = None
    try:
        connection = connect()
        if args.command == "sources":
            with connection.cursor() as cursor:
                cursor.execute(
                    """SELECT s.id, s.name, s.url, s.status, s.declared_language, s.topic_hint,
                    ct.code AS default_content_type, s.terms_url, s.terms_reviewed_at
                    FROM source_channels s
                    LEFT JOIN content_types ct ON ct.id=s.default_content_type_id
                    ORDER BY s.id"""
                )
                rows = cursor.fetchall()
            print(json.dumps(rows, ensure_ascii=False, indent=2, default=str))
            if not rows:
                print("No hay canales registrados. Aplica las migraciones.")
        elif args.command == "probe":
            results = probe_candidate_channels(connection, args.source_id)
            print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
            if not results:
                print("No hay canales permitidos para la prueba. Comprueba la migración 003.")
        elif args.command == "ingest":
            results = ingest_active_channels(connection, args.source_id)
            print(json.dumps(results, ensure_ascii=False, indent=2, default=str))
            if not results:
                print("No hay canales ACTIVE registrados.")
        elif args.command == "activate":
            if not args.confirm_terms_reviewed:
                raise RuntimeError(
                    "No se activa el canal sin --confirm-terms-reviewed. "
                    "La existencia de un RSS no implica permiso de reutilización."
                )
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE source_channels SET status='ACTIVE',
                    terms_reviewed_at=UTC_TIMESTAMP(6)
                    WHERE id=%s AND status='PAUSED'""",
                    (args.source_id,),
                )
                changed = cursor.rowcount
            connection.commit()
            if changed != 1:
                raise RuntimeError(
                    "No se activó ningún canal: comprueba el ID y que su estado sea PAUSED."
                )
            print(f"Canal {args.source_id} activado. Ya puede incluirse en la captura.")

        elif args.command == "analyze":
            analyzer = NewsAnalyzer(connection, llm_client=None)
            count = analyzer.analyze_pending_items(limit=args.limit)
            print(f"Análisis finalizado. Noticias procesadas: {count}")
        elif args.command == "mail":
            return _cmd_mail(args, connection)
        elif args.command == "digest":
            return _cmd_digest(args, connection)
        elif args.command == "mailbox":
            return _cmd_mailbox(args, connection)
        elif args.command == "mail-check":
            return _cmd_mail_check()
        elif args.command == "profile":
            return _cmd_profile(args, connection)
        return 0

    except Exception as exc:  # noqa: BLE001 — CLI: se informa y se devuelve código 1
        if connection:
            connection.rollback()
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        if connection:
            connection.close()


def _require_legacy_mail() -> None:
    """La vía vigente es la API de OSAP; el correo solo se permite explícitamente."""
    if os.environ.get("OSAP_NEWS_LEGACY_MAIL", "").strip().lower() not in {"1", "true", "yes", "si", "sí"}:
        raise RuntimeError(
            "La integración vigente es la API de OSAP (/noticias): OSAP resuelve la "
            "identidad y el consentimiento. Para usar el flujo histórico de correo, "
            "define OSAP_NEWS_LEGACY_MAIL=1 de forma consciente."
        )

def _cmd_mail(args, connection) -> int:
    """Responde a un correo (o a una consulta directa) con noticias por temas."""
    _require_legacy_mail()
    from .news_service import enqueue_response, handle_raw_message, handle_topics
    from .settings import load_settings

    settings = load_settings()

    if args.eml:
        from pathlib import Path

        raw = Path(args.eml).read_bytes()
        response = handle_raw_message(
            raw, connection, settings, persist=True,
            limit=args.limit, window_days=args.days,
        )
    elif args.sender and args.topics:
        topics = [t.strip() for t in args.topics.split(",") if t.strip()]
        response = handle_topics(
            args.sender, topics, language=args.lang, limit=args.limit,
            window_days=args.days, connection=connection, settings=settings,
            build_message=True,
        )
    else:
        raise RuntimeError("Indica --eml o, en su lugar, --from y --topics.")

    data = response.as_dict()
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))

    if args.save and response.message:
        from pathlib import Path

        Path(args.save).write_text(response.message.as_string(), encoding="utf-8")
        print(f"Respuesta guardada en {args.save}")

    if args.queue != "NONE" and response.message:
        # ai_noticias no envía: deja el mensaje preparado para que OSAP lo envíe.
        token = enqueue_response(response, connection, args.queue)
        print(f"Entrega {args.queue}: {token}")
    return 0


def _cmd_digest(args, connection) -> int:
    """Proceso periódico: capturar noticias y enviar el boletín a cada suscriptor."""
    _require_legacy_mail()
    from .digest import run_digest
    from .settings import load_settings

    settings = load_settings()
    report = run_digest(
        connection,
        settings,
        do_ingest=not args.no_ingest,
        delivery=args.delivery,
        window_days=args.days,
        only_user=args.user,
        dry_run=args.dry_run,
        address_override=args.to,
        topics_override=None,
        language_override=args.lang,
    )
    print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2, default=str))
    return 0 if report.failed == 0 else 2


def _cmd_mailbox(args, connection) -> int:
    """Procesa el correo recibido y deja las respuestas preparadas."""
    _require_legacy_mail()
    from .mailbox import process_directory, process_stdin
    from .settings import load_settings

    settings = load_settings()
    if args.stdin:
        response = process_stdin(connection, settings, args.delivery)
        print(json.dumps(response.as_dict(), ensure_ascii=False, indent=2, default=str))
        return 0
    if not args.dir:
        raise RuntimeError("Indica --dir o --stdin.")

    result = process_directory(args.dir, connection, settings, args.delivery)
    print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2, default=str))
    return 0 if result.failed == 0 else 2


def _cmd_mail_check() -> int:
    """Diagnóstico del módulo y del catálogo OSAP."""
    from .news_service import describe_vocabulary
    from .settings import load_settings

    settings = load_settings()
    print(json.dumps({
        "envio": "delegado en osap-support (cola outbound_messages, ADR-006)",
        "remitente_configurado": settings.mail.from_address,
        "idioma_por_defecto": settings.default_language,
        "ventana_dias": settings.default_window_days,
        "max_items": settings.max_items,
        "remitentes_permitidos": list(settings.allowed_senders),
        "dominios_permitidos": list(settings.allowed_domains),
    }, ensure_ascii=False, indent=2))
    print("catálogo OSAP:", json.dumps(describe_vocabulary(settings), ensure_ascii=False))
    return 0


def _cmd_profile(args, connection) -> int:
    """Alta o consulta de un perfil de usuario con sus temas de interés."""
    from . import profiles as profiles_repo

    if args.show:
        profile = profiles_repo.get_profile_by_email(connection, args.email)
        if not profile:
            print(f"No hay perfil para {args.email}.")
            return 1
        print(json.dumps(profile.as_dict(), ensure_ascii=False, indent=2))
        return 0

    topics = [t.strip() for t in (args.topics or "").split(",") if t.strip()]
    profile_id = profiles_repo.create_profile(
        connection, address=args.email, display_name=args.name,
        language=args.lang, topics=topics,
    )
    if topics:
        profiles_repo.set_topics(connection, profile_id, topics)
    connection.commit()
    profile = profiles_repo.get_profile_by_email(connection, args.email)
    print(json.dumps(profile.as_dict() if profile else {"id": profile_id},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
