import pytest

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


@pytest.mark.parametrize(
    "config",
    [
        ProjectConfig("portal", ProjectType.FRONTEND, frontend=Frontend.REACT),
        ProjectConfig("portal", ProjectType.FRONTEND, frontend=Frontend.ANGULAR),
        ProjectConfig(
            "api",
            ProjectType.API,
            api=ApiFramework.FASTAPI,
            database=Database.NONE,
        ),
        ProjectConfig(
            "api",
            ProjectType.API,
            api=ApiFramework.EXPRESS,
            database=Database.MYSQL,
        ),
        ProjectConfig(
            "fullstack",
            ProjectType.FULLSTACK,
            frontend=Frontend.REACT,
            api=ApiFramework.FASTAPI,
            database=Database.NONE,
        ),
        ProjectConfig(
            "fullstack",
            ProjectType.FULLSTACK,
            frontend=Frontend.ANGULAR,
            api=ApiFramework.EXPRESS,
            database=Database.MYSQL,
        ),
        ProjectConfig(
            "painel",
            ProjectType.WEB_APP,
            web_framework=WebFramework.FLASK,
            database=Database.MYSQL,
        ),
    ],
)
def test_accepts_configurations_for_each_project_type(
    config: ProjectConfig,
) -> None:
    assert config.name


@pytest.mark.parametrize(
    "arguments",
    [
        {
            "name": "portal",
            "project_type": ProjectType.FRONTEND,
            "frontend": Frontend.REACT,
            "database": Database.MYSQL,
        },
        {
            "name": "api",
            "project_type": ProjectType.API,
            "api": ApiFramework.FASTAPI,
        },
        {
            "name": "fullstack",
            "project_type": ProjectType.FULLSTACK,
            "frontend": Frontend.REACT,
            "database": Database.NONE,
        },
        {
            "name": "painel",
            "project_type": ProjectType.WEB_APP,
            "web_framework": WebFramework.FLASK,
            "api": ApiFramework.FASTAPI,
            "database": Database.NONE,
        },
    ],
)
def test_rejects_fields_incompatible_with_project_type(
    arguments: dict[str, object],
) -> None:
    with pytest.raises(ProjectConfigError):
        ProjectConfig(**arguments)  # type: ignore[arg-type]


@pytest.mark.parametrize("name", ["sentinel", "meu-projeto", "api_2026"])
def test_accepts_safe_project_names(name: str) -> None:
    validate_project_name(name)


@pytest.mark.parametrize(
    "name",
    [
        "",
        ".",
        "..",
        "../teste",
        "../../teste",
        "/tmp/teste",
        "C:\\teste",
        "teste/outro",
        "teste\\outro",
    ],
)
def test_rejects_unsafe_project_names(name: str) -> None:
    with pytest.raises(ProjectConfigError):
        validate_project_name(name)


@pytest.mark.parametrize("name", ["CON", "nul", "COM1", "LPT9"])
def test_rejects_windows_reserved_names(name: str) -> None:
    with pytest.raises(ProjectConfigError):
        validate_project_name(name)
