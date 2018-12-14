from ..connectors import Database
bulletin_replacements_SQLCreateQuery = """CREATE TABLE IF NOT EXISTS bulletin_replacements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site INTEGER NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,

    FOREIGN KEY (site) REFERENCES bulletin_sites (id)
);
"""

bulletin_notices_SQLCreateQuery = """CREATE TABLE IF NOT EXISTS bulletin_notices(
    notice INTEGER NOT NULL,
    site INTEGER NOT NULL,

    FOREIGN KEY (notice) REFERENCES notices (id)
    FOREIGN KEY (site) REFERENCES bulletin_sites (id)
);
"""


def getNoticesMatchingSite(siteID: int = None):

    if siteID is None:
        result = Database.fetchAll(
            """SELECT notice, site FROM bulletin_notices""")
        sites = {}
        for notice, site in result:
            if site not in sites:
                sites[site] = []
            sites[site].append(notice)
        return sites
    else:
        result = Database.fetchAll("""SELECT notice
            FROM bulletin_notices
            WHERE site = ?
            """, (siteID,))
        print(result)
        return result


def getSitesMatchingNotice(noticeID: int = None):
    if noticeID is None:
        result = Database.fetchAll(
            """SELECT notice, site FROM bulletin_notices""")
        notices = {}
        for notice, site in result:
            if notice not in notices:
                notices[notice] = []
            notices[notice].append(site)
        return notices
    else:
        result = Database.fetchAll("""SELECT notice
            FROM bulletin_notices
            WHERE notice = ?
            """, (noticeID,))
        print(result)
        return result
