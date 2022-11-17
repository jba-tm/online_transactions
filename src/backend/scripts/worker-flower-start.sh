#! /usr/bin/env bash
set -e

# Let the DB start
poetry run python -m app.celeryworker_pre_start
poetry run celery -A app.worker flower --port=5555
