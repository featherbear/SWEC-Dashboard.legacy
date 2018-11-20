from ...auth import AUTH_TYPE, User
from ...connectors import Database
from ...auth import PEM
from tornado.httputil import HTTPServerRequest
from tornado.escape import json_decode
from ... import audit
from time import time
import sys

from tornado.escape import json_encode
from tornado.web import authenticated

from ..SiteHandler import routing
from ...jinja2_integration import BaseHandler


def errorJSON(errString):
    return json_encode({'error': errString})


@routing.GET("/dashboard/admin/users")
def auditRedirect(self: BaseHandler, path):
    return self.redirect("/" + path + "/")


@routing.GET("/dashboard/admin/users/")
@routing.GET("/dashboard/admin/users/index.(?:php|html?)")
@authenticated
def auditHome(self: BaseHandler, path):
    return self.render_jinja2("/dashboard/admin/users.html", permissionsMap=permissionsMapJSON())


@routing.POST("/dashboard/admin/users/create")
@authenticated
def userCreate(self: BaseHandler, path):
    if not self.current_user.userHasPermission(PEM.SITE_ADMIN):
        return self.write_error(403)

    postArgs = json_decode(self.request.body)
    un = postArgs['username']
    pw = postArgs['password']

    result = False
    if not Database.fetchOne(
            """
            SELECT id 
            FROM users
            WHERE username = ? and userType = ?
            """,
            (un, AUTH_TYPE.AUTH_USER)):
        result = Database.insert(
            """
            INSERT INTO 
                users (username, password, userType, {}, {}, {}, {}) 
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """.format(
                PEM.SITE_LOGIN, PEM.SITE_ADMIN, PEM.NOTICE_POST, PEM.NOTICE_MODIFY),
            (un, pw, AUTH_TYPE.AUTH_USER, 1, 0, 1, 0)
        )

    if result:
        audit.log(audit.action.USER_ADD,
                  self.current_user, result, int(time()))
    return self.write(json_encode(dict(status=bool(result))))


@routing.POST("/dashboard/admin/users/delete")
@authenticated
def userDelete(self: BaseHandler, path):
    if not self.current_user.userHasPermission(PEM.SITE_ADMIN):
        return self.write_error(403)

    postArgs = json_decode(self.request.body)
    id = postArgs['id']

    # Has to be local user, and not superuser
    if id == 0 or User(id).type != AUTH_TYPE.AUTH_USER:
        return self.write_error(406)

    result = False

    result = Database.update(
        """
        DELETE FROM users
        WHERE id = ?
        """, (id,))

    if result:
        audit.log(audit.action.USER_PASSWORD,
                  self.current_user, id, int(time()))

    return self.write(json_encode(dict(status=bool(result))))


@routing.POST("/dashboard/admin/users/password")
@authenticated
def userPassword(self: BaseHandler, path):
    postArgs = json_decode(self.request.body)
    id = postArgs['id']

    # Has to be admin or own account
    if not self.current_user.userHasPermission(PEM.SITE_ADMIN) or self.current_user.id != id:
        return self.write_error(403)

    # Has to be local user, and not superuser
    if id == 0 or User(id).type != AUTH_TYPE.AUTH_USER:
        return self.write_error(406)

    newPass = postArgs['password']

    if id == self.current_user.id:
        result = Database.update(
            """
            UPDATE users 
            SET password = ?
            WHERE
            id = ?, password = ?
            """, (newPass, id, postArgs['oldPassword'])
        )
    else:
        result = Database.update(
            """
            UPDATE users 
            SET password = ?
            WHERE
            id = ?
            """, (newPass, id)
        )

    if result:
        audit.log(audit.action.USER_PASSWORD,
                  self.current_user, id, int(time()))
    return self.write(json_encode(dict(status=bool(result))))


# print(list(map(lambda pem: getattr(PEM, pem), filter(lambda e: not e.startswith("_"), dir(PEM)))))

@routing.POST("/dashboard/admin/users/permission")
@authenticated
def userPermission(self: BaseHandler, path):
    # Has to be admin, and not superuser
    if not self.current_user.userHasPermission(PEM.SITE_ADMIN):
        return self.write_error(403)

    postArgs = json_decode(self.request.body)
    id = postArgs['id']

    # Also, can't modify your own perms
    # TODO FIX
    if int(id) == 0 or int(id) == int(self.current_user.id):
        return self.write_error(406)

    result = [False]

    def checkAndUpdate(permission, auditA, auditB):
        arg = postArgs.get(permission, None)

        if arg is not None:
            if not Database.update(
                    """
                    UPDATE users 
                    SET {} = ?
                    WHERE
                    id = ?
                    """.format(permission), (bool(arg), id)
            ):
                raise Exception()
            audit.log(auditA if arg else auditB, self.current_user, id)
            result[0] = True

    try:
        checkAndUpdate(PEM.SITE_LOGIN, audit.action.USER_ACTIVE,
                       audit.action.USER_LOCK)
        checkAndUpdate(PEM.SITE_ADMIN, audit.action.USER_ADMIN_PROMOTE,
                       audit.action.USER_ADMIN_DEMOTE)
        checkAndUpdate(PEM.NOTICE_POST, audit.action.NOTICE_CAN_POST,
                       audit.action.NOTICE_CANNOT_POST)
        checkAndUpdate(PEM.NOTICE_MODIFY, audit.action.NOTICE_CAN_MODIFY,
                       audit.action.NOTICE_CANNOT_MODIFY)
    except Exception as e:
        result[0] = False
    finally:
        return self.write(json_encode(dict(status=result[0])))


permissionColumns = (
    *map(lambda obj: obj[1], Database.fetchAll("PRAGMA table_info(users)")[6:]),)
permissionsMap = dict(enumerate(permissionColumns))
permissionsReverseMap = {}
for key, val in permissionsMap.items():
    permissionsReverseMap[val] = key
permissionsMap.update(permissionsReverseMap)


@routing.GET("/dashboard/admin/users/permissions.json")
def permissionsMapJSON():
    return json_encode(permissionsMap)


@routing.POST("/dashboard/admin/users/data.json")
def fetchMore(self: BaseHandler, path):
    # Gets rows from the present to past
    queryStart = time()

    postArgs = json_decode(self.request.body)
    start = postArgs.get("startIndex", 0)
    amount = postArgs.get("amount", 10)

    results = Database.fetchAll("SELECT * from users")

    # id userType username password firstName lastName pem_login pem_noticePost, pem_noticeModify pem_siteAdmin
    # Remove password
    passwordColumn = 3
    # dataNoPassword = [(*entry[:passwordColumn], *entry[passwordColumn + 1:]) for entry in results]

    dataNoPassword = [list(entry) for entry in results]
    for entry in dataNoPassword:
        del entry[passwordColumn]

    # id userType username firstName lastName pem_login pem_noticePost, pem_noticeModify pem_siteAdmin

    # sort by getFullName()
    data = sorted(dataNoPassword, key=lambda entry: User(
        entry[0]).getFullName())

    # Start from index `start` and get `amount` records
    data = data[start:start + amount]

    timeTaken = time() - queryStart

    result = dict(
        results=[dict(
            name=User(record[0]).getFullName(),
            id=record.pop(0),
            userType=record.pop(0),
            username=record.pop(0),
            firstName=record.pop(0),
            lastName=record.pop(0),
            permissions=record
        ) for record in data],
        count=len(data),
        nextRow=start + len(data),
        generated=timeTaken,
    )

    return self.finish(json_encode(result))
