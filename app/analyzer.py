"""Lógica de análisis editorial e IA para ai_noticias."""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
import os

from typing import Any

from .db import transaction
from .llm_client import create_llm_client

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class NewsAnalyzer:
    def __init__(self, connection):
        self.connection = connection
        # Configurar el cliente IA basado en el proveedor y API del archivo osap.toml
        llm_provider = os.getenv('OSAP_API_LLM_PROVIDER', 'gemini')
        api_key = os.getenv('GEMINI_API') if llm_provider == 'gemini' else os.getenv('GROQ_API')
        self.llm_client = create_llm_client(llm_provider, api_key)
        self.prompt_version = "v1.0"
        self.model_name = f"{llm_provider}-v1"

    def analyze_pending_items(self, limit: int = 10) -> int:
        """Busca noticias capturadas sin análisis y las procesa."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT ni.id, np.title_original, np.description_original, np.language_declared, 
                       np.id as publication_id, so.id as observation_id, so.content_hash
                FROM news_items ni
                JOIN news_publications np ON ni.primary_publication_id = np.id
                JOIN source_observations so ON so.news_publication_id = np.id
                LEFT JOIN analysis_runs ar ON ar.news_item_id = ni.id AND ar.status = 'SUCCESS'
                WHERE so.processing_status = 'CAPTURED'
                  AND ar.id IS NULL
                ORDER BY ni.first_detected_at DESC
                LIMIT %s
                """, (limit,))
            items = cursor.fetchall()

        count = 0
        for item in items:
            if self._analyze_item(item):
                count += 1
        return count

    def _analyze_item(self, item: dict) -> bool:
        """Realiza el análisis de una noticia individual."""
        logger.info(f"Analizando noticia {item['id']}: {item['title_original'][:50]}...")

        # 1. Crear el run de análisis
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO analysis_runs (news_item_id, provider, model, prompt_version, status, created_at)
                VALUES (%s, %s, %s, %s, 'PENDING', %s)
                """, (item['id'], self.model_name, self.model_name, self.prompt_version, _utcnow()))
            run_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO analysis_inputs (analysis_run_id, news_publication_id, content_hash, input_role)
                VALUES (%s, %s, %s, 'PRIMARY')
                """, (run_id, item['publication_id'], item['content_hash'],))

        self.connection.commit()

        # 2. Llamar a la IA
        try:
            result = self._call_llm(item)
            self._persist_analysis_result(run_id, item, result)
            return True
        except Exception as e:
            logger.error(f"Error analizando {item['id']}: {e}")
            with self.connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE analysis_runs SET status = 'FAILED', error_message = %s, finished_at = %s
                    WHERE id = %s
                    """, (str(e), _utcnow(), run_id))
            self.connection.commit()
            return False

    def _call_llm(self, item: dict) -> dict:
        """
        Enviar prompt al modelo y recibir el JSON real desde LLM Client.
        """
        return self.llm_client.analyze({
            "title": item["title_original"],
            "description": item["description_original"]
        })

    def _persist_analysis_result(self, run_id: int, item: dict, result: dict):
        """Guarda el resultado del análisis en las tablas correspondientes."""
        now = _utcnow()
        with self.connection.cursor() as cursor:
            with transaction(self.connection):
                # 1. Actualizar el run
                cursor.execute(
                    """
                    UPDATE analysis_runs 
                    SET status = 'SUCCESS', finished_at = %s, raw_response = %s
                    WHERE id = %s
                    """, (now, json.dumps(result), run_id))

                # 2. Crear editorial_analyses
                cursor.execute("SELECT id FROM content_types WHERE code = %s", (result['content_type'],))
                ct_row = cursor.fetchone()
                ct_id = ct_row['id'] if ct_row else None

                cursor.execute(
                    """
                    INSERT INTO editorial_analyses 
                    (analysis_run_id, is_relevant, content_type_id, language_detected, 
                     relevance_reason, confidence, needs_review, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (run_id, result['relevant'], ct_id, result['language_detected'],
                          result['relevance_reason'], result['confidence'], result['needs_review'], now))
                analysis_id = cursor.lastrowid

                # 3. Crear editorial_texts
                if result['relevant']:
                    cursor.execute(
                        """
                        INSERT INTO editorial_texts (news_item_id, editorial_analysis_id, language_code, title, summary, status, created_at)
                        VALUES (%s, %s, 'es', %s, %s, 'DRAFT', %s)
                        """, (item['id'], analysis_id, result['editorial_title_es'], result['summary_es'], now))

                # 4. Actualizar estado de la observación
                cursor.execute(
                    """
                    UPDATE source_observations SET processing_status = 'ANALYZED'
                    WHERE id = %s
                    """, (item['observation_id'],))

        self.connection.commit()
