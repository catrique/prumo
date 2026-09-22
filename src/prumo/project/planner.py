"""Plan and create the initial project directory structure."""

from dataclasses import dataclass
from pathlib import Path

from prumo.project.config import ProjectConfig, ProjectType, validate_project_name

_FRONTEND_DIRECTORY = "frontend"
_BACKEND_DIRECTORY = "backend"


@dataclass(frozen=True, slots=True)
class ProjectPlan:
    """Directory structure calculated for a project."""

    root: str
    project_type: ProjectType
    directories: tuple[str, ...]


class ProjectTargetExistsError(FileExistsError):
    """Raised when the project destination already exists."""


def plan_project(config: ProjectConfig) -> ProjectPlan:
    """Calculate the project layout without touching the filesystem."""
    directories = (
        (_FRONTEND_DIRECTORY, _BACKEND_DIRECTORY)
        if config.project_type is ProjectType.FULLSTACK
        else ()
    )
    return ProjectPlan(
        root=config.name,
        project_type=config.project_type,
        directories=directories,
    )


def frontend_target_directory(plan: ProjectPlan, project_root: Path) -> Path:
    """Resolve the directory where planned frontend content belongs."""
    if _FRONTEND_DIRECTORY in plan.directories:
        return project_root / _FRONTEND_DIRECTORY

    return project_root


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
