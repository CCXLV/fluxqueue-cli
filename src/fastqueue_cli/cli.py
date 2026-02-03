import re
from typing import Annotated

import typer

from fastqueue_cli.exceptions import InvalidVersionError
from fastqueue_cli.worker import download_and_install

app = typer.Typer()
worker_app = typer.Typer()

app.add_typer(worker_app, name="worker")


@worker_app.command(name="install")
def worker_install(
    version: Annotated[
        str | None,
        typer.Option(
            help="Specify a version to install. If not provided, installs the latest version."
        ),
    ] = None,
):
    """
    Download and install [bold]FastQueue Worker[/bold].
    """
    if version:
        pattern = r"^\d+\.\d+\.\d+$"

        if not re.match(pattern, version):
            raise InvalidVersionError(
                "Invalid version. Please use versions like: 0.1.0, 0.2.3"
            )

    download_and_install(version)


@worker_app.command(name="update")
def worker_update(
    version: Annotated[
        str | None,
        typer.Option(
            help="Specify a version to update to. If not provided, updates to the latest version."
        ),
    ] = None,
    no_backup: Annotated[
        bool,
        typer.Option(
            help="Do not save the old version binary when updating. Default behavior saves it."
        ),
    ] = False,
):
    pass


if __name__ == "__main__":
    app()
