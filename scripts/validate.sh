#!/usr/bin/env bash
set -e

echo "==> Starting containers..."
docker compose up -d

echo "==> Waiting for PostgreSQL to be ready..."
docker exec -i tfm_postgres bash -c "until pg_isready -U admin -d tfm_dw; do sleep 2; done"

echo "==> Running PostgreSQL minimal validation..."
docker exec -i tfm_postgres psql -U admin -d tfm_dw -f /docker-entrypoint-initdb.d/03_validation.sql

echo "==> Running MongoDB minimal validation..."
docker exec -i tfm_mongodb mongosh -u admin -p admin123 --authenticationDatabase admin --quiet --eval '
  const dbApi = db.getSiblingDB("tfm_api");
  print("collections:", dbApi.getCollectionNames());
  print("teams_count:", dbApi.teams.countDocuments());
  print("matches_count:", dbApi.matches.countDocuments());
'

echo "==> OK: local reproducibility validation completed."