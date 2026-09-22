"""Project configuration and validation rules."""

import re
from dataclasses import dataclass
from enum import StrEnum

_PROJECT_NAME_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
_MAX_PROJECT_NAME_LENGTH = 255
_WINDOWS_RESERVED_NAMES = {
    "AUX",
    "CON",
    "NUL",
    "PRN",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


class ProjectConfigError(ValueError):
    """Raised when a project configuration is invalid."""


class ProjectType(StrEnum):
    """Top-level project types offered by Prumo."""

    FRONTEND = "Frontend"
    API = "API"
    FULLSTACK = "Fullstack"
    WEB_APP = "Aplicação web"


class Frontend(StrEnum):
    """Frontend frameworks understood by Prumo."""

    REACT = "React"
    ANGULAR = "Angular"


class ApiFramework(StrEnum):
    """Frameworks intended specifically for APIs."""

    FASTAPI = "FastAPI"
    EXPRESS = "Express"


class WebFramework(StrEnum):
    """Frameworks intended for server-side web applications."""

    FLASK = "Flask"


class Database(StrEnum):
    """Database choices understood by Prumo."""

    NONE = "Nenhum"
    MYSQL = "MySQL"


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    """Validated choices for a project."""

    name: str
    project_type: ProjectType
    frontend: Frontend | None = None
    api: ApiFramework | None = None
    web_framework: WebFramework | None = None
    database: Database | None = None

    def __post_init__(self) -> None:
        validate_project_name(self.name)
        validate_project_components(self)


def validate_project_name(name: str) -> None:
    """Ensure a name is a safe, portable directory name."""
    if not name:
        raise ProjectConfigError("o nome não pode ser vazio.")

    if len(name) > _MAX_PROJECT_NAME_LENGTH:
        raise ProjectConfigError(
            f"o nome deve ter no máximo {_MAX_PROJECT_NAME_LENGTH} caracteres."
        )

    if not _PROJECT_NAME_PATTERN.fullmatch(name):
        raise ProjectConfigError(
            "use apenas letras, números, hífen e sublinhado, começando por "
            "letra ou número."
        )

    if name.upper() in _WINDOWS_RESERVED_NAMES:
        raise ProjectConfigError("esse nome é reservado pelo sistema operacional.")


def validate_project_components(config: ProjectConfig) -> None:
    """Ensure that only fields relevant to the project type are populated."""
    if config.project_type is ProjectType.FRONTEND:
        if config.frontend is None:
            raise ProjectConfigError("um projeto frontend exige um framework.")
        if any((config.api, config.web_framework, config.database)):
            raise ProjectConfigError("frontend não aceita backend ou banco de dados.")
        return

    if config.project_type is ProjectType.API:
        if config.api is None or config.database is None:
            raise ProjectConfigError("uma API exige tecnologia e escolha de banco.")
        if config.frontend is not None or config.web_framework is not None:
            raise ProjectConfigError("API não aceita frontend ou aplicação web.")
        return

    if config.project_type is ProjectType.FULLSTACK:
        if (
            config.frontend is None
            or config.api is None
            or config.database is None
        ):
            raise ProjectConfigError(
                "fullstack exige frontend, backend/API e escolha de banco."
            )
        if config.web_framework is not None:
            raise ProjectConfigError("fullstack não aceita framework de aplicação web.")
        return

    if config.web_framework is None or config.database is None:
        raise ProjectConfigError(
            "aplicação web exige framework e escolha de banco."
        )
    if config.frontend is not None or config.api is not None:
        raise ProjectConfigError(
            "aplicação web não aceita frontend ou API separados."
        )


def unavailable_generators(config: ProjectConfig) -> tuple[str, ...]:
    """Return selected technologies whose generators are not implemented."""
    if config.project_type is ProjectType.FRONTEND:
        return () if config.frontend is Frontend.REACT else (Frontend.ANGULAR.value,)

    if config.project_type is ProjectType.API:
        return (config.api.value,) if config.api is not None else ()

    if config.project_type is ProjectType.FULLSTACK:
        unavailable = []
        if config.frontend is Frontend.ANGULAR:
            unavailable.append(Frontend.ANGULAR.value)
        if config.api is not None:
            unavailable.append(config.api.value)
        return tuple(unavailable)

    return (
        (config.web_framework.value,)
        if config.web_framework is not None
        else ()
    )
