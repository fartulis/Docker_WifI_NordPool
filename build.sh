#!/usr/bin/env bash
# build.sh v3.1
set -e
mkdir -p data
docker compose up --build
