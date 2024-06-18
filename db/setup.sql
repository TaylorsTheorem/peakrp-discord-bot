CREATE TABLE IF NOT EXISTS user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  discord_id INTEGER NOT NULL UNIQUE,
  joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS support_case (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  discord_id INTEGER NOT NULL,
  type INTEGER NOT NULL,
  title TEXT,
  description TEXT,
  rating INTEGER,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  finished_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS support_case_supporter (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  support_case_id INTEGER NOT NULL,
  supporter_id INTEGER,
  is_primary BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS case_types (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  type TEXT NOT NULL
);

INSERT INTO case_types (type) VALUES ('ic');
INSERT INTO case_types (type) VALUES ('voice');
INSERT INTO case_types (type) VALUES ('donator');
INSERT INTO case_types (type) VALUES ('frak');
INSERT INTO case_types (type) VALUES ('unban');
INSERT INTO case_types (type) VALUES ('refund');
INSERT INTO case_types (type) VALUES ('stream');
INSERT INTO case_types (type) VALUES ('support');
INSERT INTO case_types (type) VALUES ('complaint');
INSERT INTO case_types (type) VALUES ('application');