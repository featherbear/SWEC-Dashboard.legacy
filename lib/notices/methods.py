from .Notice import Notice
from ..connectors import Database

from ..auth import User, PEM


def getNotice(id) -> Notice:
    loader = Database.fetchOne(
        "SELECT title, description, author, date, endDate, priority, added, approved, active FROM notices WHERE id = ?",
        (id,))
    if loader:
        notice = Notice(*loader)
        notice.id = id
        return notice
    return None


def submitNotice(title, description, author, date, endDate=None, priority=0, active=1) -> Notice:
    from time import time

    if not endDate:
        endDate = date

    time = int(time())
    isApproved = User(author).userHasPermission(PEM.NOTICE_MODIFY)
    entry = Database.insert(
        """
        INSERT INTO notices 
            (title, description, author, date, endDate, priority, added, approved, active) 
        VALUES 
            (?,     ?,           ?,      ?,    ?,       ?,        ?,     ?       , ?)
        """,
        (title, description, author, date, endDate, priority, time, isApproved, active))
    notice = Notice(title, description, author, date, endDate,
                    priority, time, isApproved, active)
    notice.id = entry
    return notice


def editNotice(id: int, data: dict, sites: list = None):
    # extract only items from `data` which have a non-None value
    data = dict(filter(lambda pair: pair[1], data.items()))

    try:

        if sites:
            if not Database.update("""
            DELETE FROM bulletin_notices
            WHERE notice = ?
            """, (id,), commit=False):
                raise Exception()

            for site in sites:
                if not Database.insert("""INSERT 
                INTO bulletin_notices (notice, site)
                VALUES (?, ?)""", (id, site), commit=False):
                    raise Exception()

        result = Database.update(
            """
            UPDATE notices 
            SET {}
            WHERE
            id = ?
            """.format(", ".join(map(lambda k: k + " = ?", data.keys()))), (*data.values(), id,), commit=False
        )
        if not result:
            raise Exception()

        Database.conn.commit()
        return result
    except:
        Database.conn.rollback()
        return False


def approveNotice(id: int):
    return Database.update(
        """
        UPDATE notices 
          SET approved = 1
        WHERE
          id = ?
        """, (id,)
    )


def deleteNotice(id: int):
    return Database.update(
        """
        DELETE FROM notices 
        WHERE
          id = ?
        """, (id,)
    )


def toggleNotice(id: int, turnOn):
    return Database.update(
        """
        UPDATE notices 
          SET active = ?
        WHERE
          id = ?
        """, (turnOn, id)
    )


def fetch(start: int, number: int, uid=None, showPending=False, showInactive=False):
    WHERE = []
    if not showPending:
        WHERE.append(
            "(notices.approved = 1 OR notices.author = {})".format(uid))
    if not showInactive:
        WHERE.append("notices.active = 1")
    WHERE = ("WHERE " + " AND ".join(WHERE)) if WHERE else ""

    return Database.fetchAll("""
                                SELECT notices.*, users.userType, users.username, users.firstName, users.lastName
                                FROM notices
                                LEFT JOIN users on users.id = notices.author
                                 {} 
                                LIMIT ?, ?""".format(WHERE), (start, number))
