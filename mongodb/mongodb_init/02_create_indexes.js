// 02_create_indexes.js

db = db.getSiblingDB("tfm_api");

db.matches.createIndex({ match_date: 1 });
db.teams.createIndex({ team_name: 1 }, { unique: true });

print("Indexes created.");