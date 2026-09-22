import subprocess
from pathlib import Path
from typing import Any

import pytest

from prumo.generators import react
from prumo.generators.react import (
    ReactDependencyInstallError,
    ReactScaffoldError,
    generate_react_project,
)


def test_generate_react_runs_vite_and_install_without_shell(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[list[str], dict[str, Any]]] = []

    def record_run(arguments: list[str], **options: Any) -> None:
        calls.append((arguments, options))

    monkeypatch.setattr(react.subprocess, "run", record_run)

    generate_react_project(tmp_path, Path("npm.cmd"))

    assert calls == [
        (
            [
                "npm.cmd",
                "create",
                "vite@latest",
                ".",
                "--",
                "--template",
                "react-ts",
                "--no-interactive",
            ],
            {"cwd": tmp_path, "check": True, "shell": False},
        ),
        (
            ["npm.cmd", "install"],
            {"cwd": tmp_path, "check": True, "shell": False},
        ),
    ]


def test_generate_react_does_not_install_after_vite_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    def fail_run(_arguments: list[str], **_options: object) -> None:
        nonlocal calls
        calls += 1
        raise subprocess.CalledProcessError(returncode=1, cmd="npm")

    monkeypatch.setattr(react.subprocess, "run", fail_run)

    with pytest.raises(ReactScaffoldError):
        generate_react_project(tmp_path, Path("npm.cmd"))

    assert calls == 1


def test_generate_react_reports_dependency_install_failure(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    def fail_second_run(_arguments: list[str], **_options: object) -> None:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise subprocess.CalledProcessError(returncode=1, cmd="npm install")

    monkeypatch.setattr(react.subprocess, "run", fail_second_run)

    with pytest.raises(ReactDependencyInstallError):
        generate_react_project(tmp_path, Path("npm.cmd"))

    assert calls == 2
