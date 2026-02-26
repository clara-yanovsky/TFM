-- 01_schema.sql
-- Esquema mínimo reproducible para evaluación local

CREATE TABLE IF NOT EXISTS team (
  team_id SERIAL PRIMARY KEY,
  team_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS competition (
  competition_id SERIAL PRIMARY KEY,
  competition_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS match (
  match_id SERIAL PRIMARY KEY,
  match_date DATE NOT NULL,
  competition_id INT REFERENCES competition(competition_id)
);

CREATE TABLE IF NOT EXISTS match_team (
  match_id INT REFERENCES match(match_id),
  team_id INT REFERENCES team(team_id),
  goals_for INT NOT NULL,
  goals_against INT NOT NULL,
  result TEXT NOT NULL,
  PRIMARY KEY (match_id, team_id)
);