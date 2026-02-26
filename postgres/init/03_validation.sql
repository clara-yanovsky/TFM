-- 03_validation.sql
-- Validación mínima para evaluación local

-- Verificar cantidad de equipos
SELECT 'team_count' AS check_name, COUNT(*) AS value
FROM team;

-- Verificar cantidad de partidos
SELECT 'match_count' AS check_name, COUNT(*) AS value
FROM match;

-- Consulta representativa: últimos partidos de Brazil
SELECT 
    t.team_name,
    m.match_date,
    mt.goals_for,
    mt.goals_against,
    mt.result
FROM match_team mt
JOIN team t ON t.team_id = mt.team_id
JOIN match m ON m.match_id = mt.match_id
WHERE t.team_name = 'Brazil'
ORDER BY m.match_date DESC;