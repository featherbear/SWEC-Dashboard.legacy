sermons_SQLCreateQuery = """CREATE TABLE IF NOT EXISTS sermons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    site INTEGER NOT NULL,
    date TEXT NOT NULL,
    
    title TEXT NOT NULL,
    passage TEXT NOT NULL,
    speaker TEXT NOT NULL,
    outline TEXT NOT NULL,
    
    FOREIGN KEY (site) REFERENCES sites (id)
);
"""

from ..connectors import Database


def getSermon(id: int):
    return Database.fetchOne("SELECT * FROM sermons WHERE id = ?", (id,))


def getSermons(start: int = None, count: int = None):
    if start and count:
        result = Database.fetchAll("SELECT * FROM sermons ORDER BY id DESC LIMIT ?, ?", (start, count))
    else:
        result = Database.fetchAll("SELECT * FROM sermons ORDER BY id DESC")
    return result
