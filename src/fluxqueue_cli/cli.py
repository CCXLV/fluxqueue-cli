import re
from typing import Annotated

import typer

from fluxqueue_cli.exceptions import InvalidVersionError
from fluxqueue_cli.worker import (
    download_and_install,
    start_worker,
    update_worker,
)

app = typer.Typer()
worker_app = typer.Typer()

app.add_typer(worker_app, name="worker", help="Worker related commands.")


@app.command()
def start(
    *,
    concurrency: Annotated[
        int,
        typer.Option(
            "--concurrency",
            "-c",
            envvar="fluxqueue_CONCURRENCY",
            help="Number of tasks to run in parallel.",
        ),
    ] = 4,
    redis_url: Annotated[
        str,
        typer.Option(
            "--redis-url",
            "-r",
            envvar="fluxqueue_REDIS_URL",
            help="Redis URL for the worker to connect to.",
        ),
    ] = "redis://127.0.0.1:6379",
    tasks_module_path: Annotated[
        str,
        typer.Option(
            "--tasks-module-path",
            "-t",
            envvar="fluxqueue_TASKS_MODULE_PATH",
            help="Module path where the task functions are exported or located.",
        ),
    ],
    queue: Annotated[
        str,
        typer.Option(
            "--queue",
            "-q",
            envvar="fluxqueue_QUEUE",
            help="Name of the queue.",
        ),
    ] = "default",
    save_dead_tasks: Annotated[
        bool,
        typer.Option(
            is_flag=True,
            help="Saves dead tasks in Redis that have used all their retries yet still failed. Can be useful for debugging.",
        ),
    ] = False,
):
    """
    Start a [bold]fluxqueue[/bold] worker.
    """
    start_worker(
        concurrency=concurrency,
        redis_url=redis_url,
        tasks_module_path=tasks_module_path,
        queue=queue,
        save_dead_tasks=save_dead_tasks,
    )


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
    Download and install [bold]fluxqueue-worker[/bold].
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
            help="Do not save the old version binary when updating. Default behavior saves it.",
        ),
    ] = False,
):
    """
    Update [bold]fluxqueue-worker[/bold].
    """
    update_worker(version=version, no_backup=no_backup)


if __name__ == "__main__":
    app()
