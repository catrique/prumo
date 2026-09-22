from typer.testing import CliRunner

from prumo import __version__
from prumo.cli import app

runner = CliRunner()


def test_help_displays_prumo_presentation() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Prumo" in result.output
    assert "version" in result.output


def test_version_displays_current_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert result.output == f"Prumo {__version__}\n"


def test_unknown_command_returns_error_exit_code() -> None:
    result = runner.invoke(app, ["unknown"])

    assert result.exit_code != 0
