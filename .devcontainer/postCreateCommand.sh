#!/bin/bash

git config --global --add safe.directory /smart-home

pre-commit install --install-hooks

rye run migrate
rye run loaddata users board iot storage
