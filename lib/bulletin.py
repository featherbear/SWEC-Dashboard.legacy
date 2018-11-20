bulletin_replacements_SQLCreateQuery = """CREATE TABLE IF NOT EXISTS bulletin_replacements(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	site INTEGER NOT NULL,
	key TEXT NOT NULL,
	value TEXT NOT NULL,

	FOREIGN KEY (site) REFERENCES bulletin_sites (id)
);
"""