-- 02_seed.sql
-- Datos mínimos para validación

INSERT INTO team (team_name) VALUES
('Brazil'),
('Germany')
ON CONFLICT DO NOTHING;

INSERT INTO competition (competition_name) VALUES
('FIFA World Cup')
ON CONFLICT DO NOTHING;

-- Insertar partido
INSERT INTO match (match_date, competition_id)
SELECT '2024-06-15', competition_id
FROM competition
WHERE competition_name = 'FIFA World Cup'
ON CONFLICT DO NOTHING;

-- Insertar estadísticas del partido
INSERT INTO match_team (match_id, team_id, goals_for, goals_against, result)
SELECT m.match_id, t.team_id, 2, 1, 'W'
FROM match m, team t
WHERE m.match_date = '2024-06-15'
AND t.team_name = 'Brazil'
ON CONFLICT DO NOTHING;

INSERT INTO match_team (match_id, team_id, goals_for, goals_against, result)
SELECT m.match_id, t.team_id, 1, 2, 'L'
FROM match m, team t
WHERE m.match_date = '2024-06-15'
AND t.team_name = 'Germany'
ON CONFLICT DO NOTHING;