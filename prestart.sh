#!/usr/bin/env bash

sleep 10
python manage.py migrate
python manage.py collectstatic --noinput
