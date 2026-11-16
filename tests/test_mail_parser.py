# -*- coding: utf-8 -*-
"""Pruebas del parser de correo: temas, idioma, limites y campos clave: valor."""
import unittest
from email import policy
from email.parser import BytesParser

from app.mail_parser import detect_language, parse_message, parse_topics

OPERA = "\u00f3pera"
INVESTIGACION = "investigaci\u00f3n"
ESPANOL = "espa\u00f1ol"
FRANCES = "fran\u00e7ais"
PEREZ = "P\u00e9rez"


class TopicParsingTests(unittest.TestCase):
    def test_comma_separated_topics(self):
        self.assertEqual(
            parse_topics(f"jazz, {OPERA}, patrimonio"),
            ["jazz", OPERA, "patrimonio"],
        )

    def test_split_on_newlines_and_semicolons(self):
        self.assertEqual(
            parse_topics(f"jazz\n{INVESTIGACION}; musica coral"),
            ["jazz", INVESTIGACION, "musica coral"],
        )

    def test_split_on_conjunction(self):
        self.assertEqual(parse_topics("jazz y blues"), ["jazz", "blues"])

    def test_discards_conversational_text(self):
        topics = parse_topics(
            f"Hola, me interesan noticias sobre jazz. Responde en ingl\u00e9s"
        )
        self.assertIn("jazz", topics)
        self.assertNotIn("Hola", topics)
        self.assertFalse(any("responde" in t.lower() for t in topics))

    def test_leading_filler_is_removed(self):
        self.assertEqual(parse_topics("quiero noticias sobre jazz"), ["jazz"])
        self.assertEqual(parse_topics(f"me interesa la {OPERA}"), [OPERA])
        self.assertEqual(parse_topics("me interesan las noticias sobre jazz"), ["jazz"])

    def test_discards_long_sentences(self):
        topics = parse_topics(
            "quiero recibir informaci\u00f3n sobre la historia de la m\u00fasica"
        )
        self.assertEqual(topics, [])

    def test_keeps_short_music_terms(self):
        self.assertEqual(parse_topics(f"{OPERA}, jazz"), [OPERA, "jazz"])

    def test_deduplicates(self):
        self.assertEqual(parse_topics("Jazz, jazz, JAZZ"), ["Jazz"])

    def test_strips_list_markers(self):
        self.assertEqual(parse_topics("- jazz\n- opera\n* blues"), ["jazz", "opera", "blues"])


class LanguageTests(unittest.TestCase):
    def test_explicit_language_field(self):
        self.assertEqual(detect_language("idioma: fr")[0], "fr")

    def test_in_english_phrase(self):
        self.assertEqual(detect_language("send me news about jazz in English")[0], "en")

    def test_en_espanol(self):
        self.assertEqual(detect_language(f"responder en {ESPANOL}")[0], "es")

    def test_accented_language_name(self):
        self.assertEqual(detect_language(f"r\u00e9ponds en {FRANCES}")[0], "fr")

    def test_default_language(self):
        self.assertEqual(detect_language("jazz", "es")[0], "es")

    def test_topic_is_not_a_language(self):
        # «en musicolog\u00eda» o «in jazz» no deben cambiar el idioma.
        self.assertEqual(detect_language("noticias en musicolog\u00eda", "es")[0], "es")
        self.assertEqual(detect_language("news in jazz", "es")[0], "es")


def parse(raw: str):
    """Parsea como lo hace el buzón: desde bytes y con policy.default."""
    message = BytesParser(policy=policy.default).parsebytes(raw.encode("utf-8"))
    return parse_message(message)


class MessageParsingTests(unittest.TestCase):
    RAW = (
        f"From: Ana {PEREZ} <ana@example.org>\n"
        "Subject: Noticias de jazz\n"
        "Message-ID: <abc@example.org>\n"
        "MIME-Version: 1.0\n"
        "Content-Type: text/plain; charset=utf-8\n"
        "\n"
        f"temas: jazz, {OPERA}\n"
        "idioma: en\n"
        "limite: 5\n"
        "dias: 90\n"
    )

    def test_key_value_fields(self):
        request = parse(self.RAW)
        self.assertEqual(request.topics, ["jazz", OPERA])
        self.assertEqual(request.language, "en")
        self.assertEqual(request.limit, 5)
        self.assertEqual(request.window_days, 90)

    def test_sender_and_message_id(self):
        request = parse(self.RAW)
        self.assertEqual(request.sender, "ana@example.org")
        self.assertEqual(request.sender_name, f"Ana {PEREZ}")
        self.assertEqual(request.message_id, "<abc@example.org>")

    def test_header_topics(self):
        raw = (
            "From: b@example.org\nSubject: hola\nX-Osap-Topics: jazz, blues\n"
            "X-Osap-Language: fr\n\ncuerpo\n"
        )
        request = parse(raw)
        self.assertEqual(request.topics, ["jazz", "blues"])
        self.assertEqual(request.language, "fr")

    def test_html_body_is_converted(self):
        raw = (
            "From: c@example.org\nSubject: hola\nMIME-Version: 1.0\n"
            "Content-Type: text/html; charset=utf-8\n\n"
            "<html><body><p>temas: jazz</p></body></html>\n"
        )
        request = parse(raw)
        self.assertIn("jazz", request.topics)

    def test_limit_is_clamped(self):
        raw = "From: d@example.org\nSubject: x\n\nlimite: 9999\n"
        self.assertEqual(parse(raw).limit, 100)

    def test_invalid_limit_warns(self):
        raw = "From: d@example.org\nSubject: x\n\nlimite: muchos\n"
        request = parse(raw)
        self.assertIsNone(request.limit)
        self.assertTrue(request.warnings)

    def test_subject_topics_when_body_has_none(self):
        raw = "From: e@example.org\nSubject: jazz y musicologia\n\nHola, gracias.\n"
        request = parse(raw)
        self.assertIn("jazz", request.topics)


if __name__ == "__main__":
    unittest.main()
