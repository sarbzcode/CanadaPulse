from __future__ import annotations

import json
import logging

from canadapulse.logging_config import JsonFormatter


def test_json_formatter_includes_pipeline_context() -> None:
    record = logging.LogRecord(
        name="canadapulse.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="loaded records",
        args=(),
        exc_info=None,
    )
    record.pipeline_run_id = "run-123"
    record.source_name = "bank_of_canada"

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["message"] == "loaded records"
    assert payload["pipeline_run_id"] == "run-123"
    assert payload["source_name"] == "bank_of_canada"

