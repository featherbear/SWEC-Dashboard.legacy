from .. import config
from time import time

from lib.connectors import Database
from . import AUTH_TYPE, PEM


class UserModel:
    id: int

    username: str
    type: str

    firstName: str = ""
    lastName: str = ""


class NoUserException(Exception):
    pass


class User(UserModel):
    def __init__(self, id):
        self.id = int(id)
        if self.id == 0:
            self.username = "admin"
            self.type = AUTH_TYPE.AUTH_USER
            self.firstName = "Admin"
        else:
            data = Database.fetchOne(
                "SELECT username, userType, firstName, lastName FROM users WHERE id = ?", (id,))
            if not data:
                raise NoUserException()
            self.username, self.type, self.firstName, self.lastName = data

    def getFullName(self):
        return self.username if self.type == AUTH_TYPE.AUTH_USER else (
            (self.firstName + " " + self.lastName).strip() or self.username)

    def getName(self):
        return self.username if self.type == AUTH_TYPE.AUTH_USER else (self.firstName.strip() or self.username)

    def userHasPermission(self, permission) -> bool:
        if self.id == 0:
            return True

        return not not Database.fetchOne(
            "SELECT id FROM users WHERE userType = ? AND username = ? AND {} = 1".format(
                permission),
            (self.type, self.username))

    SQLCreateQuery = """CREATE TABLE IF NOT EXISTS users (
                                            id integer PRIMARY KEY AUTOINCREMENT,

                                            userType text NOT NULL,

                                            username text NOT NULL,
                                            password text,

                                            firstName text,
                                            lastName text,

                                            {} boolean NOT NULL,
                                            {} boolean NOT NULL,
                                            {} boolean NOT NULL,
                                            {} boolean NOT NULL,
                                            {} boolean NOT NULL
                                        );""".format(PEM.SITE_LOGIN, PEM.NOTICE_POST, PEM.NOTICE_MODIFY,
                                                     PEM.SITE_ADMIN, PEM.SERMON_MANAGE)


class UserSession(User):
    expiry: str

    def __str__(self):
        return "|".join([self.type, self.username, self.expiry])

    def __init__(self, _type, _username, _expiry):
        self.type, self.username, self.expiry = map(
            lambda o: o.decode() if type(o) == bytes else o, [_type, _username, _expiry])

        if self.type == AUTH_TYPE.AUTH_USER and self.username == config["SUPERUSER"]["username"]:
            self.username = "admin"
            self.type = AUTH_TYPE.AUTH_USER
            self.firstName = "Admin"
            self.id = 0
        else:
            self.id, self.firstName, self.lastName = Database.fetchOne(
                "SELECT id, firstName, lastName FROM users WHERE userType = ? AND username = ?", (self.type, self.username))

        if int(time()) > int(self.expiry):
            raise Exception("Expired")
