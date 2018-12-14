from ...auth import PEM
from tornado.httputil import HTTPServerRequest
from tornado.web import RequestHandler, authenticated
from ...jinja2_integration import BaseHandler
from ..SiteHandler import routing
from ... import audit
from time import time
from tornado.escape import json_encode, json_decode, xhtml_escape
from ...connectors import Database


def errorJSON(errString):
    return json_encode({'error': errString})


@routing.GET("/dashboard/bulletin")
def bulletinRedirect(self: BaseHandler, path):
    return self.redirect(path + "/")


@routing.GET("/dashboard/bulletin/index.(?:php|html?)")
@routing.GET("/dashboard/bulletin/")
def bulletinHome(self: BaseHandler, path):
    print("A")
    noticesSQL = Database.fetchAll("""
        SELECT notices.title, notices.description
        FROM notices, notices_link
        WHERE
            notices.id = notices_link.notice
            
            AND notices.active = 1 
            AND notices.approved = 1 
            AND strftime('%s', DMYtoYMD(notices.date)) <= strftime('%s', date('now'))
            AND strftime('%s', DMYtoYMD(notices.endDate)) >= strftime('%s', date('now'))
        ORDER BY priority DESC, date DESC
        """)

    # AND bulletin_notices.site = 
    # date <= now <= endDate
    replacementsSQL = Database.fetchAll("""
    SELECT key, value
    FROM sites_data
    WHERE site = 1
    """)

    # Should probably reorder the date from DD/MM/YYYY to YYYY/MM/DD
    data = {}
    data.update(notices=noticesSQL,
    ADDMMYYYY="Wednesday, 22nd September 1999",
                        offertory=dict(
                            month=dict(
                                name="October",
                                actual=27652,
                                budget=30843,
                            ),
                            ytd=dict(
                                actual=308623,
                                budget=325283
                            )

                        ),
                        confession="""HAH WELL 
LEMME
TELL YOU A STORY
A STORY OF A LIL GUY 
A LIL SHEPHERD BOI
WHO ENDED UP BEING THE SAVIOUR OF THE WORLD"""
                        )
    data.update(dict(replacementsSQL))
    print("AAA")
    print(data)
    return self.render_jinja2("/dashboard/bulletin/index.html", **data)
