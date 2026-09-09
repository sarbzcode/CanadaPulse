from decimal import Decimal
from uuid import uuid4

import pytest

from canadapulse.ingestion.pipelines import LABOUR_COLUMNS, labour_row, number


def observation(value="6.5"):
    return {
        "REF_DATE": "2025-01",
        "GEO": "Canada",
        "DGUID": "country",
        "Labour force characteristics": "Unemployment rate",
        "Gender": "Total - Gender",
        "Age group": "15 years and over",
        "Statistics": "Estimate",
        "Data type": "Seasonally adjusted",
        "VALUE": value,
        "UOM": "Percent",
        "SCALAR_FACTOR": "units",
        "VECTOR": "v123",
        "COORDINATE": "1.1.1",
        "STATUS": "",
        "SYMBOL": "",
        "TERMINATED": "",
        "DECIMALS": "1",
    }


def test_revisions_keep_identity_and_preserve_dimensions():
    first = dict(
        zip(LABOUR_COLUMNS, labour_row(observation(), uuid4(), "14100287", "x.csv"), strict=True)
    )
    revision = dict(
        zip(
            LABOUR_COLUMNS,
            labour_row(observation("6.7"), uuid4(), "14100287", "x.csv"),
            strict=True,
        )
    )
    assert first["source_row_hash"] == revision["source_row_hash"]
    assert revision["value"] == Decimal("6.7")
    assert first["sex"] == "Total - Gender"
    assert first["data_type"] == "Seasonally adjusted"


def test_missing_values_remain_null():
    assert number("", nullable=True) is None
    assert number("0", nullable=True) == 0


@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity", "oops", ""])
def test_invalid_numbers_fail(value):
    with pytest.raises((ValueError, ArithmeticError)):
        number(value)


def test_invalid_date_fails():
    row = observation()
    row["REF_DATE"] = "2025-99"
    with pytest.raises(ValueError):
        labour_row(row, uuid4(), "14100287", "x.csv")
