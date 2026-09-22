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


class Frontend(StrEnum):
    """Frontend choices supported by Prumo."""

    REACT = "React"
    ANGULAR = "Angular"
    NONE = "Nenhum"


class Backend(StrEnum):
    """Backend choices supported by Prumo."""

    FLASK = "Flask"
    NONE = "Nenhum"


class Database(StrEnum):
    """Database choices understood by Prumo."""

    MYSQL = "MySQL"
    NONE = "Nenhum"


@dataclass(frozen=True, slots=True)
class ProjectConfig:
    """Validated choices for a project."""

    name: str
    frontend: Frontend
    backend: Backend
    database: Database

    def __post_init__(self) -> None:
        validate_project_name(self.name)
        validate_project_components(self.frontend, self.backend, self.database)


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


def validate_project_components(
    frontend: Frontend,
    backend: Backend,
    database: Database,
) -> None:
    """Ensure the selected technologies form a supported project."""
    if frontend is Frontend.NONE and backend is Backend.NONE:
        raise ProjectConfigError("selecione ao menos um frontend ou backend.")

    if database is not Database.NONE and backend is Backend.NONE:
        raise ProjectConfigError("um banco de dados exige um backend.")
