# tol-lab-share

Rabbitmq consumer for TOL data input


## Getting Started

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


### Setting up with Docker

If you want to setup a local development environment with Docker please check
the instructions in [SETUP_DOCKER.md](SETUP_DOCKER.md)


## Running

1. Enter the python virtual environment using:
```bash
    pipenv shell
```

1. Run the app using:

```bash
    python tol-lab-share
```

## Testing

Run the tests using pytest (flags are for verbose and exit early):

```bash
    python -m pytest -vx
```

## Deployment

This project uses a Docker image as the unit of deployment. Update `.release-version` with
major/minor/patch. On merging a pull request into *develop* or *master*, a release will be created
along with the Docker image associated to that release.
