"""Interactive project creation command."""

from pathlib import Path

import typer

from prumo.commands.prompts import PromptCancelled, prompt_project_config
from prumo.generators.react import (
    ReactDependencyInstallError,
    ReactScaffoldError,
    generate_react_project,
)
from prumo.node import (
    NodePrerequisiteError,
    NodeToolchain,
    detect_node_toolchain,
    format_node_version,
)
from prumo.project.config import (
    ProjectConfig,
    ProjectType,
    unavailable_generators,
)
from prumo.project.planner import (
    ProjectPlan,
    ProjectTargetExistsError,
    create_project_structure,
    frontend_target_directory,
    plan_project,
)


def create() -> None:
    """Configure e crie um projeto com o Prumo."""
    try:
        config = prompt_project_config()
    except PromptCancelled:
        typer.echo("Operação cancelada.")
        return

    plan = plan_project(config)
    _show_summary(config)
    _stop_if_generator_is_unavailable(config)

    if not typer.confirm("Continuar?", default=True):
        typer.echo("Operação cancelada.")
        return

    toolchain = _prepare_react_toolchain()

    try:
        project_root = create_project_structure(plan)
    except ProjectTargetExistsError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from None

    _generate_react(plan, project_root, toolchain)
    _show_react_success(plan)


def _show_summary(config: ProjectConfig) -> None:
    fields: list[tuple[str, str]] = [
        ("Nome", config.name),
        ("Tipo", config.project_type.value),
    ]

    if config.project_type is ProjectType.FRONTEND:
        fields.append(("Framework", str(config.frontend)))
    elif config.project_type is ProjectType.API:
        fields.extend(
            (("Backend", str(config.api)), ("Banco", str(config.database)))
        )
    elif config.project_type is ProjectType.FULLSTACK:
        fields.extend(
            (
                ("Frontend", str(config.frontend)),
                ("Backend", str(config.api)),
                ("Banco", str(config.database)),
            )
        )
    else:
        fields.extend(
            (
                ("Framework", str(config.web_framework)),
                ("Banco", str(config.database)),
            )
        )

    typer.echo("\nProjeto")
    typer.echo("-" * 28)
    for label, value in fields:
        typer.echo(f"{label + ':':<12}{value}")
    typer.echo()


def _stop_if_generator_is_unavailable(config: ProjectConfig) -> None:
    unavailable = unavailable_generators(config)
    if not unavailable:
        return

    if len(unavailable) == 1:
        message = (
            f"o gerador {unavailable[0]} ainda não está disponível "
            "nesta versão do Prumo."
        )
    else:
        technologies = " e ".join(unavailable)
        message = (
            f"os geradores {technologies} ainda não estão disponíveis "
            "nesta versão do Prumo."
        )

    typer.echo(f"A configuração foi reconhecida, mas {message}", err=True)
    typer.echo("\nNenhum arquivo foi criado.", err=True)
    raise typer.Exit(code=1)


def _prepare_react_toolchain() -> NodeToolchain:
    try:
        toolchain = detect_node_toolchain()
    except NodePrerequisiteError as error:
        typer.echo(str(error), err=True)
        typer.echo("\nNenhum arquivo foi criado.", err=True)
        raise typer.Exit(code=1) from None

    typer.echo(
        f"[OK] Node.js encontrado ({format_node_version(toolchain.node_version)})"
    )
    typer.echo("[OK] npm encontrado")
    return toolchain


def _generate_react(
    plan: ProjectPlan,
    project_root: Path,
    toolchain: NodeToolchain,
) -> None:
    target_directory = frontend_target_directory(plan, project_root)

    try:
        generate_react_project(target_directory, toolchain.npm_executable)
    except ReactScaffoldError as error:
        typer.echo(str(error), err=True)
        typer.echo(
            "A estrutura inicial foi mantida e npm install não foi executado.",
            err=True,
        )
        raise typer.Exit(code=1) from None
    except ReactDependencyInstallError as error:
        typer.echo(str(error), err=True)
        typer.echo(
            f"Execute npm install em '{_frontend_relative_path(plan)}' "
            "para tentar novamente.",
            err=True,
        )
        raise typer.Exit(code=1) from None

    typer.echo("[OK] Projeto React criado")
    typer.echo("[OK] Dependências instaladas")


def _show_react_success(plan: ProjectPlan) -> None:
    typer.echo("\nProjeto criado com sucesso.")
    typer.echo("\nPara iniciar:")
    typer.echo(f"cd {_frontend_relative_path(plan)}")
    typer.echo("npm run dev")


def _frontend_relative_path(plan: ProjectPlan) -> Path:
    return frontend_target_directory(plan, Path(plan.root))
