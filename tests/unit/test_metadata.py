from __future__ import annotations

import pytest

from canadapulse.database.metadata import PipelineRunCounts, PipelineRunStatus
from canadapulse.exceptions import PipelineMetadataError


def test_pipeline_run_status_values_match_database_constraint() -> None:
    assert {status.value for status in PipelineRunStatus} == {
        "RUNNING",
        "SUCCESS",
        "FAILED",
        "PARTIAL",
    }


def test_pipeline_run_counts_cannot_be_negative() -> None:
    with pytest.raises(PipelineMetadataError, match="records_loaded"):
        PipelineRunCounts(records_extracted=10, records_loaded=-1, records_rejected=0)

