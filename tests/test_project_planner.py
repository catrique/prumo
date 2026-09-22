from pathlib import Path

import pytest

from prumo.project.config import Backend, Database, Frontend, ProjectConfig
from prumo.project.planner import (
    ProjectKind,
    ProjectTargetExistsError,
    create_project_structure,
    plan_project,
)


def make_config(
    frontend: Frontend,
    backend: Backend,
    database: Database = Database.NONE,
) -> ProjectConfig:
    return ProjectConfig(
        name="sentinel",
        frontend=frontend,
        backend=backend,
        database=database,
    )


@pytest.mark.parametrize("frontend", [Frontend.REACT, Frontend.ANGULAR])
def test_frontend_only_is_planned_at_project_root(frontend: Frontend) -> None:
    plan = plan_project(make_config(frontend, Backend.NONE))

    assert plan.kind is ProjectKind.FRONTEND
    assert plan.directories == ()


def test_backend_only_is_planned_at_project_root() -> None:
    plan = plan_project(make_config(Frontend.NONE, Backend.FLASK))

    assert plan.kind is ProjectKind.BACKEND
    assert plan.directories == ()


@pytest.mark.parametrize("frontend", [Frontend.REACT, Frontend.ANGULAR])
def test_fullstack_plan_separates_frontend_and_backend(frontend: Frontend) -> None:
    plan = plan_project(make_config(frontend, Backend.FLASK))

    assert plan.kind is ProjectKind.FULLSTACK
    assert plan.directories == ("frontend", "backend")


def test_create_project_structure_creates_only_planned_directories(
    tmp_path: Path,
) -> None:
    plan = plan_project(make_config(Frontend.REACT, Backend.FLASK, Database.MYSQL))

    target = create_project_structure(plan, tmp_path)

    assert target == tmp_path / "sentinel"
    assert sorted(path.name for path in target.iterdir()) == ["backend", "frontend"]
    assert all(path.is_dir() for path in target.iterdir())


def test_existing_destination_is_not_modified(tmp_path: Path) -> None:
    target = tmp_path / "sentinel"
    target.mkdir()
    existing_file = target / "important.txt"
    existing_file.write_text("preserve", encoding="utf-8")
    plan = plan_project(make_config(Frontend.REACT, Backend.FLASK))

    with pytest.raises(ProjectTargetExistsError):
        create_project_structure(plan, tmp_path)

    assert existing_file.read_text(encoding="utf-8") == "preserve"
    assert list(target.iterdir()) == [existing_file]
