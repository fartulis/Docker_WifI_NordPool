#!/usr/bin/env bash
# build.sh — Build and run all Docker services (v3.0)
set -e

# Ensure data directory exists
mkdir -p data

# Build and start containers
docker compose up --build
