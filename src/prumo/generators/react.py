"""React project generation with Vite."""

import subprocess
from pathlib import Path

_VITE_CREATE_ARGUMENTS = (
    "create",
    "vite@latest",
    ".",
    "--",
    "--template",
    "react-ts",
    "--no-interactive",
)


class ReactScaffoldError(RuntimeError):
    """Raised when Vite cannot scaffold the React project."""


class ReactDependencyInstallError(RuntimeError):
    """Raised when npm cannot install the React project dependencies."""


def generate_react_project(target_directory: Path, npm_executable: Path) -> None:
    """Create a React TypeScript project and install its dependencies."""
    try:
        subprocess.run(
            [str(npm_executable), *_VITE_CREATE_ARGUMENTS],
            cwd=target_directory,
            check=True,
            shell=False,
        )
    except (OSError, subprocess.CalledProcessError):
        raise ReactScaffoldError(
            "Não foi possível criar o projeto React com o Vite."
        ) from None

    try:
        subprocess.run(
            [str(npm_executable), "install"],
            cwd=target_directory,
            check=True,
            shell=False,
        )
    except (OSError, subprocess.CalledProcessError):
        raise ReactDependencyInstallError(
            "O projeto React foi criado, mas a instalação das dependências falhou."
        ) from None
