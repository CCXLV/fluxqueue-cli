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
            envvar="FLUXQUEUE_CONCURRENCY",
            help="Number of tasks to run in parallel.",
        ),
    ] = 4,
    redis_url: Annotated[
        str,
        typer.Option(
            "--redis-url",
            "-r",
            envvar="FLUXQUEUE_REDIS_URL",
            help="Redis connection URL for the worker.",
        ),
    ] = "redis://127.0.0.1:6379",
    tasks_module_path: Annotated[
        str,
        typer.Option(
            "--tasks-module-path",
            "-t",
            envvar="FLUXQUEUE_TASKS_MODULE_PATH",
            help="Python module path where task functions are defined (e.g. src.tasks).",
        ),
    ],
    queue: Annotated[
        str,
        typer.Option(
            "--queue",
            "-q",
            envvar="FLUXQUEUE_QUEUE",
            help="Queue name the worker reads jobs from.",
        ),
    ] = "default",
    save_dead_tasks: Annotated[
        bool,
        typer.Option(
            is_flag=True,
            help="Keep failed tasks that reached the retry limit so you can inspect them later.",
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
            help="Version to install. If omitted, installs the latest."
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
            help="Version to update to. If omitted, updates to the latest."
        ),
    ] = None,
    no_backup: Annotated[
        bool,
        typer.Option(
            is_flag=True,
            flag_value=False,
            help="Skip keeping a backup of the old binary when updating.",
        ),
    ] = False,
):
    """
    Update [bold]fluxqueue-worker[/bold].
    """
    update_worker(version=version, no_backup=no_backup)


if __name__ == "__main__":
    app()
