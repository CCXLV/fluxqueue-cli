import logging
import re
from typing import Annotated

import typer

from fastqueue_cli.worker import download_and_install

app = typer.Typer()
worker_app = typer.Typer()

app.add_typer(worker_app, name="worker")

logger = logging.getLogger(__name__)


@worker_app.command(name="install")
def worker_install(
    version: Annotated[
        str | None,
        typer.Option(
            help="Exact version of the worker you want to install (e.g 0.1.0, 0.2.3)."
        ),
    ] = None,
):
    """
    Download and install [bold]FastQueue Worker[/bold].
    """
    if version:
        pattern = r"^\d+\.\d+\.\d+$"

        if not re.match(pattern, version):
            raise Exception(
                "Invalid version. Please use versions like: 0.1.0, 0.2.3"
            )

    # TODO: Check if its already installed or not,
    # if it is just print it and add `update` command to update the version
    # NOTE: --version argument should force it
    download_and_install(version)


if __name__ == "__main__":
    app()
