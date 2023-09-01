#!/bin/bash

git config --global --add safe.directory /workspace

pipx install poetry
pipx install pre-commit

poetry install
pre-commit install --install-hooks

poetry run python ./manage.py migrate
poetry run python ./manage.py loaddata users board iot storage
