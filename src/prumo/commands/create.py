"""Interactive project creation command."""

from enum import StrEnum
from typing import TypeVar

import typer

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

    try:
        create_project_structure(plan)
    except ProjectTargetExistsError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from None

    typer.echo("Projeto criado.")


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
