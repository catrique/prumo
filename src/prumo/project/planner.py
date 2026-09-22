"""Plan and create the initial project directory structure."""

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from prumo.project.config import Backend, Frontend, ProjectConfig, validate_project_name


class ProjectKind(StrEnum):
    """Structural kinds supported by Prumo."""

    FRONTEND = "Frontend"
    BACKEND = "Backend"
    FULLSTACK = "Fullstack"


@dataclass(frozen=True, slots=True)
class ProjectPlan:
    """Directory structure calculated for a project."""

    root: str
    kind: ProjectKind
    directories: tuple[str, ...]


class ProjectTargetExistsError(FileExistsError):
    """Raised when the project destination already exists."""


def plan_project(config: ProjectConfig) -> ProjectPlan:
    """Calculate the project layout without touching the filesystem."""
    has_frontend = config.frontend is not Frontend.NONE
    has_backend = config.backend is not Backend.NONE

    if has_frontend and has_backend:
        kind = ProjectKind.FULLSTACK
        directories = ("frontend", "backend")
    elif has_frontend:
        kind = ProjectKind.FRONTEND
        directories = ()
    else:
        kind = ProjectKind.BACKEND
        directories = ()

    return ProjectPlan(root=config.name, kind=kind, directories=directories)


def create_project_structure(
    plan: ProjectPlan,
    base_directory: Path | None = None,
) -> Path:
    """Create only the directories described by a project plan."""
    validate_project_name(plan.root)
    base = Path.cwd() if base_directory is None else base_directory
    target = base.resolve() / plan.root

    try:
        target.mkdir(exist_ok=False)
    except FileExistsError:
        raise ProjectTargetExistsError(
            f"O destino '{plan.root}' já existe. Nenhum arquivo foi alterado."
        ) from None

    for directory in plan.directories:
        (target / directory).mkdir()

    return target
