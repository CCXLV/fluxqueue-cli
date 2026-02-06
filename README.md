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
fluxqueue start --tasks-module-path src.tasks
```

## Documentation

For more information and documenation about the usage please visit [**FluxQueue Documentation**](https://fluxqueue.ccxlv.dev).

## License

FluxQueue is licensed under the Apache-2.0 license. See [LICENSE](LICENSE) for details.
