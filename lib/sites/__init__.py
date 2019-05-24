from ..connectors import Database

sites_SQLCreateQuery = """CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
"""

sites_data_SQLCreateQuery = """CREATE TABLE IF NOT EXISTS sites_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,

    FOREIGN KEY (site) REFERENCES sites (id)
);
"""


def getSites():
    result = Database.fetchAll("SELECT * FROM sites")
    return dict(result) if result else False
