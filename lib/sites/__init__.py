sites_SQLCreateQuery = """CREATE TABLE IF NOT EXISTS sites (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL
);
"""

from ..connectors import Database
def getSites():
	result = Database.fetchAll("SELECT * FROM bulletin_sites")
	return dict(result) if result else False