"""Interactive menu prompts used by Prumo commands."""

from collections.abc import Callable
from enum import StrEnum
from typing import TypeVar, cast

import questionary
import typer

from prumo.project.config import (
    ApiFramework,
    Database,
    Frontend,
    ProjectConfig,
    ProjectConfigError,
    ProjectType,
    WebFramework,
    validate_project_name,
)

MenuValue = TypeVar("MenuValue", bound=StrEnum)

_PROJECT_TYPE_OPTIONS = tuple((option.value, option) for option in ProjectType)
_FRONTEND_OPTIONS = tuple((option.value, option) for option in Frontend)
_API_OPTIONS = (
    ("FastAPI (Python)", ApiFramework.FASTAPI),
    ("Express (Node.js)", ApiFramework.EXPRESS),
)
_WEB_OPTIONS = ((WebFramework.FLASK.value, WebFramework.FLASK),)
_DATABASE_OPTIONS = tuple((option.value, option) for option in Database)


class PromptCancelled(RuntimeError):
    """Raised when the user cancels an interactive menu."""


def select_option(
    message: str,
    options: tuple[tuple[str, MenuValue], ...],
) -> MenuValue:
    """Show an arrow-key menu and return its typed value."""
    choices = [
        questionary.Choice(title=title, value=value)
        for title, value in options
    ]
    answer = questionary.select(
        message,
        choices=choices,
        qmark="?",
        pointer=">",
        use_arrow_keys=True,
        use_shortcuts=False,
        instruction="Use as setas e Enter",
    ).ask()

    if answer is None:
        raise PromptCancelled

    return cast(MenuValue, answer)


def prompt_project_config() -> ProjectConfig:
    """Collect only the choices relevant to the selected project type."""
    name = _prompt_project_name()
    project_type = select_option(
        "O que você quer criar?",
        _PROJECT_TYPE_OPTIONS,
    )
    builders: dict[ProjectType, Callable[[str], ProjectConfig]] = {
        ProjectType.FRONTEND: _prompt_frontend_config,
        ProjectType.API: _prompt_api_config,
        ProjectType.FULLSTACK: _prompt_fullstack_config,
        ProjectType.WEB_APP: _prompt_web_app_config,
    }

    try:
        return builders[project_type](name)
    except ProjectConfigError as error:
        typer.echo(f"Configuração inválida: {error}", err=True)
        raise typer.Exit(code=2) from None


def _prompt_frontend_config(name: str) -> ProjectConfig:
    frontend = select_option("Escolha o framework:", _FRONTEND_OPTIONS)
    return ProjectConfig(
        name=name,
        project_type=ProjectType.FRONTEND,
        frontend=frontend,
    )


def _prompt_api_config(name: str) -> ProjectConfig:
    api = select_option("Escolha a tecnologia da API:", _API_OPTIONS)
    database = select_option("Banco de dados:", _DATABASE_OPTIONS)
    return ProjectConfig(
        name=name,
        project_type=ProjectType.API,
        api=api,
        database=database,
    )


def _prompt_fullstack_config(name: str) -> ProjectConfig:
    frontend = select_option("Frontend:", _FRONTEND_OPTIONS)
    api = select_option("Backend/API:", _API_OPTIONS)
    database = select_option("Banco de dados:", _DATABASE_OPTIONS)
    return ProjectConfig(
        name=name,
        project_type=ProjectType.FULLSTACK,
        frontend=frontend,
        api=api,
        database=database,
    )


def _prompt_web_app_config(name: str) -> ProjectConfig:
    web_framework = select_option("Framework:", _WEB_OPTIONS)
    database = select_option("Banco de dados:", _DATABASE_OPTIONS)
    return ProjectConfig(
        name=name,
        project_type=ProjectType.WEB_APP,
        web_framework=web_framework,
        database=database,
    )


def _prompt_project_name() -> str:
    while True:
        name = typer.prompt("Nome do projeto")

        try:
            validate_project_name(name)
        except ProjectConfigError as error:
            typer.echo(f"Nome inválido: {error}", err=True)
            continue

        return name
