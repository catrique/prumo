from enum import StrEnum
from pathlib import Path

import pytest
from typer.testing import CliRunner

from prumo import __version__
from prumo.cli import app
from prumo.generators.react import ReactScaffoldError
from prumo.node import NodePrerequisiteError, NodeToolchain
from prumo.project.config import (
    ApiFramework,
    Database,
    Frontend,
    ProjectType,
    WebFramework,
)

runner = CliRunner()


def configure_menu_selections(
    monkeypatch: pytest.MonkeyPatch,
    selections: tuple[StrEnum, ...],
) -> list[tuple[str, tuple[StrEnum, ...]]]:
    selected = iter(selections)
    prompts: list[tuple[str, tuple[StrEnum, ...]]] = []

    def choose(
        message: str,
        options: tuple[tuple[str, StrEnum], ...],
    ) -> StrEnum:
        values = tuple(value for _title, value in options)
        value = next(selected)
        assert value in values
        prompts.append((message, values))
        return value

    monkeypatch.setattr("prumo.commands.prompts.select_option", choose)
    return prompts


def react_toolchain() -> NodeToolchain:
    return NodeToolchain(
        node_executable=Path("node.exe"),
        npm_executable=Path("npm.cmd"),
        node_version=(22, 12, 0),
    )


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


def test_frontend_react_reaches_existing_generator_without_irrelevant_prompts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    prompts = configure_menu_selections(
        monkeypatch,
        (ProjectType.FRONTEND, Frontend.REACT),
    )
    generated_in: list[Path] = []
    monkeypatch.setattr(
        "prumo.commands.create.detect_node_toolchain",
        react_toolchain,
    )
    monkeypatch.setattr(
        "prumo.commands.create.generate_react_project",
        lambda target, _npm: generated_in.append(target),
    )

    result = runner.invoke(app, ["create"], input="portal\ny\n")

    assert result.exit_code == 0
    assert generated_in == [tmp_path / "portal"]
    assert prompts == [
        ("O que você quer criar?", tuple(ProjectType)),
        ("Escolha o framework:", tuple(Frontend)),
    ]
    assert "Backend:" not in result.output
    assert "Banco:" not in result.output


@pytest.mark.parametrize(
    ("selections", "expected_options", "technology"),
    [
        (
            (ProjectType.FRONTEND, Frontend.ANGULAR),
            (tuple(ProjectType), tuple(Frontend)),
            "Angular",
        ),
        (
            (ProjectType.API, ApiFramework.FASTAPI, Database.MYSQL),
            (tuple(ProjectType), tuple(ApiFramework), tuple(Database)),
            "FastAPI",
        ),
        (
            (
                ProjectType.FULLSTACK,
                Frontend.REACT,
                ApiFramework.EXPRESS,
                Database.NONE,
            ),
            (
                tuple(ProjectType),
                tuple(Frontend),
                tuple(ApiFramework),
                tuple(Database),
            ),
            "Express",
        ),
        (
            (ProjectType.WEB_APP, WebFramework.FLASK, Database.MYSQL),
            (tuple(ProjectType), tuple(WebFramework), tuple(Database)),
            "Flask",
        ),
    ],
)
def test_unavailable_configuration_is_recognized_without_creating_files(
    selections: tuple[StrEnum, ...],
    expected_options: tuple[tuple[StrEnum, ...], ...],
    technology: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    prompts = configure_menu_selections(monkeypatch, selections)

    result = runner.invoke(app, ["create"], input="projeto\n")

    assert result.exit_code == 1
    assert tuple(options for _message, options in prompts) == expected_options
    assert technology in result.output
    assert "Nenhum arquivo foi criado." in result.output
    assert not (tmp_path / "projeto").exists()


def test_create_can_be_cancelled_before_environment_checks(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    configure_menu_selections(
        monkeypatch,
        (ProjectType.FRONTEND, Frontend.REACT),
    )

    result = runner.invoke(app, ["create"], input="portal\nn\n")

    assert result.exit_code == 0
    assert "Operação cancelada." in result.output
    assert not (tmp_path / "portal").exists()


def test_create_stops_before_creating_files_when_node_is_unavailable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    configure_menu_selections(
        monkeypatch,
        (ProjectType.FRONTEND, Frontend.REACT),
    )

    def fail_prerequisite_check() -> NodeToolchain:
        raise NodePrerequisiteError("Node.js não encontrado.")

    monkeypatch.setattr(
        "prumo.commands.create.detect_node_toolchain",
        fail_prerequisite_check,
    )

    result = runner.invoke(app, ["create"], input="portal\ny\n")

    assert result.exit_code == 1
    assert "Nenhum arquivo foi criado." in result.output
    assert "Traceback" not in result.output
    assert not (tmp_path / "portal").exists()


def test_create_handles_vite_failure_without_traceback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    configure_menu_selections(
        monkeypatch,
        (ProjectType.FRONTEND, Frontend.REACT),
    )
    monkeypatch.setattr(
        "prumo.commands.create.detect_node_toolchain",
        react_toolchain,
    )

    def fail_generation(_target: Path, _npm: Path) -> None:
        raise ReactScaffoldError("Falha esperada do Vite.")

    monkeypatch.setattr(
        "prumo.commands.create.generate_react_project",
        fail_generation,
    )

    result = runner.invoke(app, ["create"], input="portal\ny\n")

    assert result.exit_code == 1
    assert "Falha esperada do Vite." in result.output
    assert "npm install não foi executado" in result.output
    assert "Traceback" not in result.output
