import re
from typing import Annotated

import typer

from fastqueue_cli.exceptions import InvalidVersionError
from fastqueue_cli.worker import download_and_install, update_worker

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
    Download and install [bold]fastqueue-worker[/bold].
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
            is_flag=True,
            flag_value=False,
            show_default=False,
            help="Do not save the old version binary when updating. Default behavior saves it.",
        ),
    ] = False,
):
    """
    Update [bold]fastqueue-worker[/bold].
    """
    update_worker(version=version, no_backup=no_backup)


if __name__ == "__main__":
    app()
