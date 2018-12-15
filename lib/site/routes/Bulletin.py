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


from datetime import datetime
# def NextDate(day: int):
#     # 0 - 6
#     date_today = datetime.date.today()
#     date_next = date_today + datetime.timedelta((day - date_today.weekday()) % 7)
#     return date_next


@routing.GET("/dashboard/bulletin/index.(?:php|html?)")
@routing.GET("/dashboard/bulletin/")
def bulletinHome(self: BaseHandler, path):
    id = self.get_query_argument("id", None)
    if id:
        data = Database.fetchOne("""
            SELECT title, passage, speaker, outline, site, date
            FROM sermons
            WHERE id = ?
        """, (id,))
        site = data[4]
        date = data[5]
    else:
        site = self.get_query_argument("site")
        date = self.get_query_argument("date")
        data = Database.fetchOne("""
            SELECT title, passage, speaker, outline
            FROM sermons
            WHERE site = ? AND date = ?
        """, (site, date))
    sermonData = dict(
        title = data[0],
        passage = data[1],
        speaker = data[2],
        outline = data[3]
    )
    print(sermonData)

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

    # https://stackoverflow.com/questions/5891555/display-the-date-like-may-5th-using-pythons-strftime
    dateObj = datetime.strptime(date, "%Y-%m-%d")
    def suffix(d):
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')
    dateStr = dateObj.strftime('%A, {S} %B %Y').replace('{S}', str(dateObj.day) + suffix(dateObj.day))



    # Should probably reorder the date from DD/MM/YYYY to YYYY/MM/DD
    data = {}
    data.update(notices = noticesSQL,
                ADDMMYYYY = dateStr,
                offertory = dict(
                    month = dict(
                        name = "October",
                        actual = 27652,
                        budget = 30843,
                    ),
                    ytd = dict(
                        actual = 308623,
                        budget = 325283
                    )

                ),
                confession = """HAH WELL 
LEMME
TELL YOU A STORY
A STORY OF A LIL GUY 
A LIL SHEPHERD BOI
WHO ENDED UP BEING THE SAVIOUR OF THE WORLD"""
                , bibleReading = "",
                sermonData = sermonData)
    data.update(dict(replacementsSQL))
    print("AAA")
    print(data)
    return self.render_jinja2("/dashboard/bulletin/index.html", **data)
