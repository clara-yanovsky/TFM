Write-Host "==> Starting containers..."
docker compose up -d

Write-Host "==> Waiting for PostgreSQL..."
Start-Sleep -Seconds 5

Write-Host "==> Running PostgreSQL validation..."
docker exec -i tfm_postgres psql -U admin -d tfm_dw -f /docker-entrypoint-initdb.d/03_validation.sql

Write-Host "==> Running MongoDB validation..."
docker exec -i tfm_mongodb mongosh -u admin -p admin123 --authenticationDatabase admin --quiet --eval "
  const dbApi = db.getSiblingDB('tfm_api');
  print('collections:', dbApi.getCollectionNames());
  print('teams_count:', dbApi.teams.countDocuments());
  print('matches_count:', dbApi.matches.countDocuments());
"

Write-Host "==> OK: Local reproducibility validation completed."