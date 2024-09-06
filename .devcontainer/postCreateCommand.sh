#!/bin/bash

git config --global --add safe.directory /smart-home

pre-commit install --install-hooks

uv run poe migrate
uv run poe loaddata users board iot storage

echo "MANAGE_PY_PATH=./manage.py" > .env
