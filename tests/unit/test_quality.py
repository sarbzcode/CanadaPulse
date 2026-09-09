from datetime import date

from canadapulse.validation.quality import LoadMetrics


def test_missing_values_are_measured_without_imputation():
    metrics = LoadMetrics(100, 40, 10, 50, 5, date(2025, 1, 1), date(2025, 2, 1))
    assert metrics.null_rate == 0.05
    assert metrics.inserted + metrics.updated + metrics.unchanged == metrics.loaded
