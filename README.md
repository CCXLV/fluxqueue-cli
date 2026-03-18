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

You can also install it in a custom path:

```bash
fluxqueue worker install --path .fluxqueue/
```

## Starting a Worker

To start a worker, provide the path to the module where your tasks are exported:

```bash
fluxqueue start --tasks-module-path src/tasks
```

To start the worker installed at the custom path you can do the following,
add these lines in your `pyproject.toml`:

```toml
[tool.fluxqueue_cli]
worker_path = ".fluxqueue/fluxqueue-worker"
```

Then running the command above will run that worker by default.

## Documentation

For more information and documenation about the usage please visit [FluxQueue Documentation](https://fluxqueue.ccxlv.dev).

## License

FluxQueue is licensed under the Apache-2.0 license. See [LICENSE](LICENSE) for details.
