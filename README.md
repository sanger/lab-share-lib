# lab-share-lib

Library to build consumers for the lab-share framework

## Setting up

The following tools are required for development:

- python (use pyenv or something similar to install the python version specified in the `Pipfile`)

Use pyenv or something similar to install the version of python
defined in the `Pipfile`:

```bash
    brew install pyenv
    pyenv install <python_version>
```
        
Use pipenv to install the required python packages for the application and development:

```bash
     pipenv install --dev
```

## Configuring

Run this command inside the project you want to add this library:

```bash
    pipenv install -e git+https://github.com/sanger/lab-share-lib@0.1.6#egg=lab-share-lib
```

## Getting started

Have a look at the examples at: [examples/README.md](./examples/README.md)

## Testing

Run the tests using pytest (flags are for verbose and exit early):

```bash
    python -m pytest -vx
```

