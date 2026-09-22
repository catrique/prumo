from pathlib import Path

import pytest
from typer.testing import CliRunner

from prumo import __version__
from prumo.cli import app
from prumo.generators.react import ReactScaffoldError
from prumo.node import NodePrerequisiteError, NodeToolchain

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


def test_create_fullstack_structure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(
        app,
        ["create"],
        input="sentinel\nAngular\nFlask\nMySQL\ny\n",
    )

    assert result.exit_code == 0
    assert "Estrutura:  Fullstack" in result.output
    assert "Estrutura inicial criada." in result.output
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


@pytest.mark.parametrize(
    ("user_input", "expected_directory"),
    [
        ("portal\nReact\nNenhum\nNenhum\ny\n", Path("portal")),
        ("portal\nReact\nFlask\nNenhum\ny\n", Path("portal/frontend")),
    ],
)
def test_create_generates_react_in_planned_directory(
    user_input: str,
    expected_directory: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    toolchain = NodeToolchain(
        node_executable=Path("node.exe"),
        npm_executable=Path("npm.cmd"),
        node_version=(22, 12, 0),
    )
    generated_in: list[Path] = []

    monkeypatch.setattr(
        "prumo.commands.create.detect_node_toolchain",
        lambda: toolchain,
    )
    monkeypatch.setattr(
        "prumo.commands.create.generate_react_project",
        lambda target, _npm: generated_in.append(target),
    )

    result = runner.invoke(app, ["create"], input=user_input)

    assert result.exit_code == 0
    assert generated_in == [tmp_path / expected_directory]
    assert "[OK] Projeto React criado" in result.output


def test_create_stops_before_creating_files_when_node_is_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    def fail_prerequisite_check() -> NodeToolchain:
        raise NodePrerequisiteError("Node.js não encontrado.")

    monkeypatch.setattr(
        "prumo.commands.create.detect_node_toolchain",
        fail_prerequisite_check,
    )

    result = runner.invoke(
        app,
        ["create"],
        input="portal\nReact\nNenhum\nNenhum\ny\n",
    )

    assert result.exit_code == 1
    assert "Nenhum arquivo foi criado." in result.output
    assert "Traceback" not in result.output
    assert not (tmp_path / "portal").exists()


def test_create_handles_vite_failure_without_traceback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    toolchain = NodeToolchain(
        node_executable=Path("node.exe"),
        npm_executable=Path("npm.cmd"),
        node_version=(22, 12, 0),
    )

    monkeypatch.setattr(
        "prumo.commands.create.detect_node_toolchain",
        lambda: toolchain,
    )

    def fail_generation(_target: Path, _npm: Path) -> None:
        raise ReactScaffoldError("Falha esperada do Vite.")

    monkeypatch.setattr(
        "prumo.commands.create.generate_react_project",
        fail_generation,
    )

    result = runner.invoke(
        app,
        ["create"],
        input="portal\nReact\nNenhum\nNenhum\ny\n",
    )

    assert result.exit_code == 1
    assert "Falha esperada do Vite." in result.output
    assert "npm install não foi executado" in result.output
    assert "Traceback" not in result.output
