from lib import config
from . import PEM, AUTH_TYPE
from .User import User
from ..connectors import Database


def authenticate(username, password):
    # Cookie structure
    # AUTH_TYPE|USERNAME|EXPIRY

    if (config["SUPERUSER"]["enabled"]
            and username == config["SUPERUSER"]["username"]
            and password == config["SUPERUSER"]["password"]):
        return 0

    uid = Database.fetchOne("SELECT id FROM users WHERE userType = ? AND username = ? AND password = ?",
                            (AUTH_TYPE.AUTH_USER, username, password))
    if not uid:
        raise NoUserException()

    if not User(uid).userHasPermission(PEM.SITE_LOGIN):
        raise UserLockedException()

    return uid


class NoUserException(Exception):
    pass


class UserLockedException(Exception):
    pass
