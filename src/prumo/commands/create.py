"""Interactive project creation command."""

from enum import StrEnum
from pathlib import Path
from typing import TypeVar

import typer

from prumo.generators.react import (
    ReactDependencyInstallError,
    ReactScaffoldError,
    generate_react_project,
)
from prumo.node import (
    NodePrerequisiteError,
    NodeToolchain,
    detect_node_toolchain,
    format_node_version,
)
from prumo.project.config import (
    Backend,
    Database,
    Frontend,
    ProjectConfig,
    ProjectConfigError,
    validate_project_name,
)
from prumo.project.planner import (
    ProjectKind,
    ProjectPlan,
    ProjectTargetExistsError,
    create_project_structure,
    frontend_target_directory,
    plan_project,
)

Choice = TypeVar("Choice", bound=StrEnum)


def create() -> None:
    """Configure e crie a estrutura inicial de um projeto."""
    config = _prompt_config()
    plan = plan_project(config)
    _show_summary(config, plan)

    if not typer.confirm("Continuar?", default=True):
        typer.echo("Operação cancelada.")
        return

    toolchain = (
        _prepare_react_toolchain()
        if config.frontend is Frontend.REACT
        else None
    )

    try:
        project_root = create_project_structure(plan)
    except ProjectTargetExistsError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from None

    if toolchain is not None:
        _generate_react(plan, project_root, toolchain)
        _show_react_success(plan)
        return

    typer.echo("Estrutura inicial criada.")


def _prepare_react_toolchain() -> NodeToolchain:
    try:
        toolchain = detect_node_toolchain()
    except NodePrerequisiteError as error:
        typer.echo(str(error), err=True)
        typer.echo("\nNenhum arquivo foi criado.", err=True)
        raise typer.Exit(code=1) from None

    typer.echo(
        f"[OK] Node.js encontrado ({format_node_version(toolchain.node_version)})"
    )
    typer.echo("[OK] npm encontrado")
    return toolchain


def _generate_react(
    plan: ProjectPlan,
    project_root: Path,
    toolchain: NodeToolchain,
) -> None:
    target_directory = frontend_target_directory(plan, project_root)

    try:
        generate_react_project(target_directory, toolchain.npm_executable)
    except ReactScaffoldError as error:
        typer.echo(str(error), err=True)
        typer.echo(
            "A estrutura inicial foi mantida e npm install não foi executado.",
            err=True,
        )
        raise typer.Exit(code=1) from None
    except ReactDependencyInstallError as error:
        typer.echo(str(error), err=True)
        typer.echo(
            f"Execute npm install em '{_frontend_relative_path(plan)}' "
            "para tentar novamente.",
            err=True,
        )
        raise typer.Exit(code=1) from None

    typer.echo("[OK] Projeto React criado")
    typer.echo("[OK] Dependências instaladas")


def _show_react_success(plan: ProjectPlan) -> None:
    frontend_path = _frontend_relative_path(plan)
    typer.echo("\nProjeto criado com sucesso.")

    if plan.kind is ProjectKind.FULLSTACK:
        typer.echo("\nFrontend:")
        typer.echo("    frontend/")
        typer.echo("\nBackend:")
        typer.echo("    backend/")
        typer.echo("\nPara iniciar o frontend:")
        typer.echo(f"cd {frontend_path}")
        typer.echo("npm run dev")
        typer.echo("\nO backend Flask ainda não foi gerado.")
        return

    typer.echo("\nPara iniciar:")
    typer.echo(f"cd {frontend_path}")
    typer.echo("npm run dev")


def _frontend_relative_path(plan: ProjectPlan) -> Path:
    return frontend_target_directory(plan, Path(plan.root))


def _prompt_config() -> ProjectConfig:
    name = _prompt_project_name()
    frontend = _prompt_choice(
        "Frontend",
        (Frontend.REACT, Frontend.ANGULAR, Frontend.NONE),
    )
    backend = _prompt_choice("Backend", (Backend.FLASK, Backend.NONE))

    database_choices = (
        (Database.MYSQL, Database.NONE)
        if backend is Backend.FLASK
        else (Database.NONE,)
    )
    database = _prompt_choice("Banco de dados", database_choices)

    try:
        return ProjectConfig(
            name=name,
            frontend=frontend,
            backend=backend,
            database=database,
        )
    except ProjectConfigError as error:
        typer.echo(f"Configuração inválida: {error}", err=True)
        raise typer.Exit(code=2) from None


def _prompt_project_name() -> str:
    while True:
        name = typer.prompt("Nome do projeto")

        try:
            validate_project_name(name)
        except ProjectConfigError as error:
            typer.echo(f"Nome inválido: {error}", err=True)
            continue

        return name


def _prompt_choice(label: str, choices: tuple[Choice, ...]) -> Choice:
    available_values = "/".join(choice.value for choice in choices)

    while True:
        answer = typer.prompt(f"{label} [{available_values}]")

        for choice in choices:
            if answer.casefold() == choice.value.casefold():
                return choice

        typer.echo(
            f"Opção inválida. Escolha uma destas opções: {available_values}.",
            err=True,
        )


def _show_summary(config: ProjectConfig, plan: ProjectPlan) -> None:
    typer.echo("\nProjeto")
    typer.echo("-" * 28)
    typer.echo(f"Nome:       {config.name}")
    typer.echo(f"Frontend:   {config.frontend.value}")
    typer.echo(f"Backend:    {config.backend.value}")
    typer.echo(f"Banco:      {config.database.value}")
    typer.echo(f"Estrutura:  {plan.kind.value}")
    typer.echo("\nEstrutura planejada:\n")
    typer.echo(_format_tree(plan))
    typer.echo()


def _format_tree(plan: ProjectPlan) -> str:
    lines = [f"{plan.root}/"]

    if plan.directories:
        for index, directory in enumerate(plan.directories):
            connector = "`--" if index == len(plan.directories) - 1 else "|--"
            lines.append(f"{connector} {directory}/")
    else:
        content = (
            "conteúdo do frontend na raiz"
            if plan.kind is ProjectKind.FRONTEND
            else "conteúdo do backend na raiz"
        )
        lines.append(f"`-- {content}")

    return "\n".join(lines)
