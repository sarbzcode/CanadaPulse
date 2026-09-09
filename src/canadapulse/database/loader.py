"""Shared database loading helpers."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path
from typing import Any


def execute_sql_files(connection: Any, sql_files: Iterable[Path]) -> None:
    """Execute SQL files in order inside a single transaction."""

    try:
        with connection.cursor() as cursor:
            for sql_file in sql_files:
                cursor.execute(sql_file.read_text(encoding="utf-8"))
        connection.commit()
    except Exception:
        connection.rollback()
        raise

