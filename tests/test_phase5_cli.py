from typer.testing import CliRunner

from patient_sim.cli.main import app

runner = CliRunner()


def test_cli_start_help():
    result = runner.invoke(app, ["start", "--help"])
    assert result.exit_code == 0
    assert "scenario" in result.output


def test_cli_turn_help():
    result = runner.invoke(app, ["turn", "--help"])
    assert result.exit_code == 0
    assert "session_id" in result.output
