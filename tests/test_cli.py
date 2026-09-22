from pathlib import Path

import pytest
from typer.testing import CliRunner

from prumo import __version__
from prumo.cli import app

runner = CliRunner()


def test_help_displays_prumo_presentation() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Prumo" in result.output
    assert "create" in result.output
    assert "version" in result.output


def test_version_displays_current_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert result.output == f"Prumo {__version__}\n"


def test_unknown_command_returns_error_exit_code() -> None:
    result = runner.invoke(app, ["unknown"])

    assert result.exit_code != 0


def test_create_fullstack_project(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        ["create"],
        input="sentinel\nReact\nFlask\nMySQL\ny\n",
    )

    assert result.exit_code == 0
    assert "Estrutura:  Fullstack" in result.output
    assert "Projeto criado." in result.output
    assert (tmp_path / "sentinel" / "frontend").is_dir()
    assert (tmp_path / "sentinel" / "backend").is_dir()


def test_create_can_be_cancelled_without_creating_directory(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        ["create"],
        input="portal\nReact\nNenhum\nNenhum\nn\n",
    )

    assert result.exit_code == 0
    assert "Operação cancelada." in result.output
    assert not (tmp_path / "portal").exists()


def test_create_rejects_project_without_frontend_or_backend(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        ["create"],
        input="empty\nNenhum\nNenhum\nNenhum\n",
    )

    assert result.exit_code == 2
    assert "Configuração inválida:" in result.output
    assert not (tmp_path / "empty").exists()


def test_create_reprompts_after_invalid_name(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        ["create"],
        input="../fora\nportal\nReact\nNenhum\nNenhum\ny\n",
    )

    assert result.exit_code == 0
    assert "Nome inválido:" in result.output
    assert (tmp_path / "portal").is_dir()
    assert not (tmp_path.parent / "fora").exists()


def test_create_does_not_overwrite_existing_destination(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    target = tmp_path / "api"
    target.mkdir()
    marker = target / "important.txt"
    marker.write_text("preserve", encoding="utf-8")

    result = runner.invoke(
        app,
        ["create"],
        input="api\nNenhum\nFlask\nMySQL\ny\n",
    )

    assert result.exit_code == 1
    assert "já existe" in result.output
    assert marker.read_text(encoding="utf-8") == "preserve"
