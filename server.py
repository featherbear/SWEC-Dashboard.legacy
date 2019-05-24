from lib.connectors import Database
import tornado.ioloop
import tornado.web

from lib.api import APIHandler
from lib.connectors import ElvantoAuth
from lib.site import SiteHandler

app = tornado.web.Application([
    ("/api(/.*)?", APIHandler),
    ("/login/oauth", ElvantoAuth),
    ("/(.*)", SiteHandler),
],
    cookie_secret="ABC",
    # xsrf_cookies = True,
    login_url="/login/"
)


if Database.conn is not None:
    from lib.auth import UserSession

    Database.create_table(Database.conn, UserSession.SQLCreateQuery)

    from lib.notices import Notice

    Database.create_table(Database.conn, Notice.SQLCreateQuery)

    from lib.audit import auditLog_SQLCreateQuery

    Database.create_table(Database.conn, auditLog_SQLCreateQuery)

    from lib.sites import sites_SQLCreateQuery, sites_data_SQLCreateQuery

    Database.create_table(Database.conn, sites_SQLCreateQuery)
    Database.create_table(Database.conn, sites_data_SQLCreateQuery)

    from lib.notices_link import notices_link_SQLCreateQuery
    Database.create_table(Database.conn, notices_link_SQLCreateQuery)

    from lib.sermons import sermons_SQLCreateQuery
    Database.create_table(Database.conn, sermons_SQLCreateQuery)


else:
    raise Exception("Cannot create the database connection.")


PORT = 58388
app.listen(PORT)

print("Server listening on port " + str(PORT))
tornado.ioloop.IOLoop.current().start()
