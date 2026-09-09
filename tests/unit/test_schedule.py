import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "refresh_scheduled", Path(__file__).parents[2] / "scripts/refresh_scheduled.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_weekly_labour_and_weekday_rates():
    assert module.selected_sources("", 0) == ["boc"]
    assert module.selected_sources("", 4) == ["boc", "statcan"]
    assert module.selected_sources("statcan", 0) == ["statcan"]
    with pytest.raises(ValueError):
        module.selected_sources("untrusted", 0)
