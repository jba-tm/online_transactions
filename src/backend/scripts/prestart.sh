#! /usr/bin/env bash

# Let the DB start
poetry run python -m app.backend_pre_start
#
## Run migrations
poetry run alembic upgrade head
#
## Create initial data in DB
poetry run python -m app.initial_data
