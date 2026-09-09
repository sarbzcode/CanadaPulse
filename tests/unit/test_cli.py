from __future__ import annotations

import json

from canadapulse.cli import main


def test_config_command_outputs_redacted_settings(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.setenv("CANADAPULSE_DB_PASSWORD", "local-password")

    exit_code = main(["config"])
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert output["database"]["password"] == "***"

