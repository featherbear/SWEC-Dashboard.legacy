import tornado.ioloop
import tornado.web

from lib.api import APIHandler
from lib.connectors import ElvantoAuth
from lib.site import SiteHandler

if __name__ == "__main__":
    app = tornado.web.Application([
        ("/api(/.*)?", APIHandler),
        ("/login/oauth", ElvantoAuth),
        ("/(.*)", SiteHandler),
    ],
        cookie_secret="ABC",
        # xsrf_cookies = True,
        login_url="/login/"
    )

    from lib.connectors import Database

    if Database.conn is not None:
        from lib.auth import UserSession
        Database.create_table(Database.conn, UserSession.SQLCreateQuery)

        from lib.notices import Notice
        Database.create_table(Database.conn, Notice.SQLCreateQuery)

        from lib.audit import auditLog_SQLCreateQuery, fetch
        Database.create_table(Database.conn, auditLog_SQLCreateQuery)

        from lib.sites import sites_SQLCreateQuery
        Database.create_table(Database.conn, sites_SQLCreateQuery)

        from lib.bulletin import bulletin_replacements_SQLCreateQuery
        Database.create_table(Database.conn, bulletin_replacements_SQLCreateQuery)

    else:
        raise Exception("Cannot create the database connection.")

    app.listen(58388)

    tornado.ioloop.IOLoop.current().start()
