from ..connectors import Database
sermons_SQLCreateQuery = """CREATE TABLE IF NOT EXISTS sermons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    site INTEGER NOT NULL,
    date TEXT NOT NULL,
    
    title TEXT NOT NULL,
    passage TEXT NOT NULL,
    speaker TEXT NOT NULL,
    outline TEXT NOT NULL,
    
    UNIQUE (site, date),
    FOREIGN KEY (site) REFERENCES sites (id)
);
"""


def getSermon(id: int):
    return Database.fetchOne("SELECT * FROM sermons WHERE id = ?", (id,))


def getSermons(start: int = None, count: int = None):
    if start and count:
        result = Database.fetchAll(
            "SELECT * FROM sermons ORDER BY id DESC LIMIT ?, ?", (start, count))
    else:
        result = Database.fetchAll("SELECT * FROM sermons ORDER BY id DESC")
    return result


def createSermon(site, date, title, passage, speaker, outline):
    return Database.insert("""
        INSERT 
        INTO sermons (site, date, title, passage, speaker, outline)
        VALUES (?, ?, ?, ?, ?, ?)   
    """,
                           (site, date, title, passage, speaker, outline))


def editSermon(id, title, passage, speaker, outline):
    Database.update("""
        UPDATE sermons
        SET title = ?, passage = ?, speaker = ?, outline = ?
        WHERE id = ?
    """,
                    (title, passage, speaker, outline, id))
