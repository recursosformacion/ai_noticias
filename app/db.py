"""Conexión y transacciones MariaDB."""
from __future__ import annotations

from contextlib import contextmanager
import pymysql
from pymysql.cursors import DictCursor

from .config import load_config


def connect():
    return pymysql.connect(cursorclass=DictCursor, **load_config())


@contextmanager
def transaction(connection):
    try:
        yield
        connection.commit()
    except Exception:
        connection.rollback()
        raise
