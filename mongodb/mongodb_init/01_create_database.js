// 01_create_database.js

db = db.getSiblingDB("tfm_api");

db.createCollection("matches");
db.createCollection("teams");

print("Database and collections created.");