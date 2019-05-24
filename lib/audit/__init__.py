class action:
    SITE_LOGIN = 1
    NOTICE_SUBMIT = 2
    NOTICE_EDIT = 3
    NOTICE_APPROVE = 4
    NOTICE_DELETE = 5
    NOTICE_ACTIVATE = 6
    NOTICE_DEACTIVATE = 7
    BULLETIN_GENERATE = 8

    LOCATION_MANAGE = 9

    USER_ADD = 10
    USER_DELETE = 11
    USER_LOCK = 12
    USER_ACTIVE = 13
    USER_PASSWORD = 14

    USER_ADMIN_PROMOTE = 15
    USER_ADMIN_DEMOTE = 16
    NOTICE_CAN_POST = 17
    NOTICE_CANNOT_POST = 18
    NOTICE_CAN_MODIFY = 19
    NOTICE_CANNOT_MODIFY=20

    SERMON_CREATE = 21
    SERMON_EDIT = 22

    _categories: list

    # action(i) --> str
    def __new__(cls, i: int):
        return next(
            filter(
                lambda name: int(getattr(cls, name)) == int(i),
                filter(
                    lambda a: a[0] != "_",
                    dir(action)
                )
            )
            , None)


action._categories = list(filter(lambda a: a[0] != "_", dir(action)))

auditLog_SQLCreateQuery = """CREATE TABLE IF NOT EXISTS audit (
                                        id INTEGER PRIMARY KEY AUTOINCREMENT,

                                        action INTEGER NOT NULL,
                                        author INTEGER NOT NULL,
                                        data text,

                                        time DATETIME NOT NULL,

                                        FOREIGN KEY (author) REFERENCES users (id)
                                    );"""

from time import time
from typing import Union

from ..auth import UserSession
from ..connectors import Database


def log(action: int, user: Union[UserSession, int, tuple], data=None, actionTime=None):
    if not actionTime: actionTime = int(time())

    if type(user) == tuple:
        id = user[0]
    elif type(user) == UserSession:
        id = user.id
    else:
        id = user

    Database.insert(
        """
                          INSERT INTO 
                              audit (action, author, time, data) 
                          VALUES (?, ?, ?, ?)
                          """,
        (action, id, actionTime, data)
    )


def fetch(start: int, number: int):
    res = Database.fetchAll("""

                                    SELECT audit.*, users.userType, users.username, users.firstName, users.lastName
                                    FROM audit
                                    LEFT JOIN users on users.id = audit.author
                                    WHERE audit.action IN ({}) 
                                    LIMIT ?
                                """.
                            format((",".join(map(str, map(lambda s: getattr(action, s), action._categories))))),
                            (start,))
    res = res[:-number - 1:-1]
    # Get rows 1-57; then reverse and select 5
    # Faster than doing `SELECT * FROM (... LIMIT ) ORDER BY ... LIMIT
    return res


def getCount():
    result = Database.fetchOne("SELECT MAX(rowid) from audit")
    return result[0] if result else 0

