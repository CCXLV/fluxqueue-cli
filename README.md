## FluxQueue CLI

A command-line tool for installing and running [FluxQueue](https://github.com/CCXLV/fluxqueue) workers.

## Installation

```bash
pip install fluxqueue-cli
```

## Installing the Worker

Use the CLI to install the worker on your system:

```bash
fluxqueue worker install
```

## Starting a Worker

To start a worker, provide the path to the module where your tasks are defined and exported:

```bash
fluxqueue start --tasks-module-path src/tasks
```

### Options

- **`--concurrency`, `-c`** (default: `4`): Number of tasks to run in parallel.
- **`--redis-url`, `-r`** (default: `redis://127.0.0.1:6379`): Connection string for the Redis instance backing FluxQueue.
- **`--tasks-module-path`, `-t`**: Python module path where your task functions are defined (for example: `src.tasks`).
- **`--queue`, `-q`** (default: `default`): Queue name the worker reads jobs from.
- **`--save-dead-tasks`** (flag, default: `false`): When enabled, keeps failed jobs that reached the retry limit so you can inspect them later.

These options can also be set via environment variables:

- **`FLUXQUEUE_CONCURRENCY`**: Default value for `--concurrency`.
- **`FLUXQUEUE_REDIS_URL`**: Default value for `--redis-url`.
- **`FLUXQUEUE_TASKS_MODULE_PATH`**: Default value for `--tasks-module-path`.
- **`FLUXQUEUE_QUEUE`**: Default value for `--queue`.
