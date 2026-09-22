from pathlib import Path

import pytest

from prumo.project.config import (
    ApiFramework,
    Database,
    Frontend,
    ProjectConfig,
    ProjectType,
)
from prumo.project.planner import (
    ProjectTargetExistsError,
    create_project_structure,
    frontend_target_directory,
    plan_project,
)


@pytest.mark.parametrize(
    ("config", "directories"),
    [
        (
            ProjectConfig(
                "portal",
                ProjectType.FRONTEND,
                frontend=Frontend.REACT,
            ),
            (),
        ),
        (
            ProjectConfig(
                "api",
                ProjectType.API,
                api=ApiFramework.FASTAPI,
                database=Database.NONE,
            ),
            (),
        ),
        (
            ProjectConfig(
                "fullstack",
                ProjectType.FULLSTACK,
                frontend=Frontend.REACT,
                api=ApiFramework.FASTAPI,
                database=Database.MYSQL,
            ),
            ("frontend", "backend"),
        ),
    ],
)
def test_plans_structure_by_project_type(
    config: ProjectConfig,
    directories: tuple[str, ...],
) -> None:
    plan = plan_project(config)

    assert plan.project_type is config.project_type
    assert plan.directories == directories


def test_frontend_target_follows_the_plan(tmp_path: Path) -> None:
    frontend = ProjectConfig(
        "portal",
        ProjectType.FRONTEND,
        frontend=Frontend.REACT,
    )
    fullstack = ProjectConfig(
        "fullstack",
        ProjectType.FULLSTACK,
        frontend=Frontend.REACT,
        api=ApiFramework.FASTAPI,
        database=Database.NONE,
    )

    assert frontend_target_directory(plan_project(frontend), tmp_path) == tmp_path
    assert frontend_target_directory(
        plan_project(fullstack), tmp_path
    ) == tmp_path / "frontend"


def test_existing_destination_is_not_modified(tmp_path: Path) -> None:
    target = tmp_path / "portal"
    target.mkdir()
    existing_file = target / "important.txt"
    existing_file.write_text("preserve", encoding="utf-8")
    config = ProjectConfig(
        "portal",
        ProjectType.FRONTEND,
        frontend=Frontend.REACT,
    )

    with pytest.raises(ProjectTargetExistsError):
        create_project_structure(plan_project(config), tmp_path)

    assert existing_file.read_text(encoding="utf-8") == "preserve"
    assert list(target.iterdir()) == [existing_file]
