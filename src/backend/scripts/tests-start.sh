#! /usr/bin/env bash
set -e

poetry run python  -m app.tests_pre_start

bash ./test.sh "$@"
