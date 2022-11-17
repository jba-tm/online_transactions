#!/usr/bin/env bash
IFS=

docker-compose --env-file ./.env up --detach --build
