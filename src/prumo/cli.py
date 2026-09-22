"""Command-line interface for Prumo."""

import typer

from prumo import __version__
from prumo.commands.create import create

app = typer.Typer(
    name="prumo",
    help="Prumo: uma base para criar e padronizar projetos de software.",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Crie e padronize projetos de software com o Prumo."""


@app.command()
def version() -> None:
    """Exibe a versão atual do Prumo."""
    typer.echo(f"Prumo {__version__}")


app.command()(create)
