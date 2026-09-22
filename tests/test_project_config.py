import pytest

from prumo.project.config import (
    Backend,
    Database,
    Frontend,
    ProjectConfig,
    ProjectConfigError,
    validate_project_name,
)


@pytest.mark.parametrize(
    ("frontend", "backend", "database"),
    [
        (Frontend.REACT, Backend.NONE, Database.NONE),
        (Frontend.ANGULAR, Backend.NONE, Database.NONE),
        (Frontend.NONE, Backend.FLASK, Database.NONE),
        (Frontend.NONE, Backend.FLASK, Database.MYSQL),
        (Frontend.REACT, Backend.FLASK, Database.NONE),
        (Frontend.REACT, Backend.FLASK, Database.MYSQL),
        (Frontend.ANGULAR, Backend.FLASK, Database.NONE),
        (Frontend.ANGULAR, Backend.FLASK, Database.MYSQL),
    ],
)
def test_accepts_supported_configurations(
    frontend: Frontend,
    backend: Backend,
    database: Database,
) -> None:
    config = ProjectConfig(
        name="sentinel",
        frontend=frontend,
        backend=backend,
        database=database,
    )

    assert config.frontend is frontend
    assert config.backend is backend
    assert config.database is database


@pytest.mark.parametrize(
    ("frontend", "backend", "database"),
    [
        (Frontend.NONE, Backend.NONE, Database.NONE),
        (Frontend.REACT, Backend.NONE, Database.MYSQL),
        (Frontend.ANGULAR, Backend.NONE, Database.MYSQL),
    ],
)
def test_rejects_unsupported_configurations(
    frontend: Frontend,
    backend: Backend,
    database: Database,
) -> None:
    with pytest.raises(ProjectConfigError):
        ProjectConfig(
            name="sentinel",
            frontend=frontend,
            backend=backend,
            database=database,
        )


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
