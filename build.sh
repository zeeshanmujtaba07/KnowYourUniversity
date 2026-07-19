#!/usr/bin/env bash
set -o errexit

pip install -r backend_django/requirements.txt
python backend_django/manage.py collectstatic --no-input
python backend_django/manage.py migrate
