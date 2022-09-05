# Use alpine for a smaller image size and install only the required packages
FROM python:3.8-slim-buster

# > Setting PYTHONUNBUFFERED to a non empty value ensures that the python output is sent straight to
# > terminal (e.g. your container log) without being first buffered and that you can see the output
# > of your application (e.g. django logs) in real time.
# https://stackoverflow.com/a/59812588
ENV PYTHONUNBUFFERED 1

# Install required libs
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    curl \
    netcat \
    git \
    unixodbc-dev

# Install the package manager - pipenv
RUN pip install --upgrade pip && \
    pip install --no-cache-dir pipenv

# Change the working directory for all proceeding operations
#   https://docs.docker.com/develop/develop-images/dockerfile_best-practices/#workdir
WORKDIR /code

# Copy all the source to the image
COPY . .

# Install both default and dev packages so that we can run the tests against this image
RUN pipenv install --dev

