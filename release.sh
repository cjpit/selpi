#!/bin/bash
set -e

git pull

docker compose down
docker compose build
docker compose up -d
