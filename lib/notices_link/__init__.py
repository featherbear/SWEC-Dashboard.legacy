from ..connectors import Database

notices_link_SQLCreateQuery = """CREATE TABLE IF NOT EXISTS notices_link(
    notice INTEGER NOT NULL,
    site INTEGER NOT NULL,

    FOREIGN KEY (notice) REFERENCES notices (id),
    FOREIGN KEY (site) REFERENCES sites (id)
);
"""


def getNoticesMatchingSite(siteID: int = None):
    if siteID is None:
        result = Database.fetchAll(
            """SELECT notice, site FROM notices_link""")
        sites = {}
        for notice, site in result:
            if site not in sites:
                sites[site] = []
            sites[site].append(notice)
        return sites
    else:
        result = Database.fetchAll("""SELECT notice
            FROM notices_link
            WHERE site = ?
            """, (siteID,))
        return result


def getSitesMatchingNotice(noticeID: int = None):
    if noticeID is None:
        result = Database.fetchAll(
            """SELECT notice, site FROM notices_link""")
        notices = {}
        for notice, site in result:
            if notice not in notices:
                notices[notice] = []
            notices[notice].append(site)
        return notices
    else:
        result = Database.fetchAll("""SELECT notice
            FROM notices_link
            WHERE notice = ?
            """, (noticeID,))
        return result


def updateSitesForNotice(noticeID: int, sites: [int]):
    Database.update("""
    DELETE 
    FROM notices_link
    WHERE notice = ?
    """,
                    (noticeID,),
                    commit=False)
    for site in sites:
        Database.insert("""
        INSERT
        INTO notices_link (notice, site)
        VALUES (?, ?)""",
                        (noticeID, site),
                        commit=False)
    Database.conn.commit()
