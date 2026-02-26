// 03_insert_sample_data.js

db = db.getSiblingDB("tfm_api");

db.teams.insertMany([
  { team_name: "Brazil" },
  { team_name: "Germany" }
]);

db.matches.insertOne({
  match_date: new Date("2024-06-15"),
  competition: "FIFA World Cup",
  teams: [
    { team_name: "Brazil", goals_for: 2, goals_against: 1, result: "W" },
    { team_name: "Germany", goals_for: 1, goals_against: 2, result: "L" }
  ]
});

print("Sample data inserted.");