from datetime import datetime
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
def bulletinRedirectA(self: BaseHandler, path):
    return self.redirect(path + "/")


@routing.GET("/dashboard/bulletin/")
def bulletinRedirectB(self: BaseHandler, path):
    return self.redirect(path + "view/")


def getWeeklyConfession(week: int):
    assert 1 <= week <= 4
    confessionOne = """
Almighty and most merciful Father,
You have loved us with an everlasting love,
But we have gone our own way
And have rejected you in thought, word, and deed.
We are sorry for our sins
And turn away from them
For the sake of your Son who died for us,
Forgive us, cleanse us and change us.
By your Holy Spirit, enable us to live for you,
And to please you more and more;
Through Jesus Christ our Lord.
Amen.
"""
    confessionTwo = """
Most merciful God,
we humbly admit that we need your help.
We confess that we have wandered from your way:
We have done wrong, and we have failed to do what is right.
You alone can save us.
Have mercy on us:
Wipe out our sins and teach us to forgive others.
Bring forth in us the fruit of the Spirit
That we may live as disciples of Christ.
This we ask in the name of Jesus our Saviour.
Amen.
"""
    confessionThree = """
Heavenly Father,
We praise you for adopting us as your children
And making us heirs of eternal life.
In your mercy you have washed us from our sins
And made us clean in your sight.
Yet we still fail to love you as we should and serve you as we ought.
Forgive us our sins and renew us by your grace,
That we may continue to grow as members of Christ,
In whom alone is our salvation.
Amen.
"""
    confessionFour = """
Merciful God, our maker and our judge, we have sinned against you in thought, word, and deed:
we have not loved you with our whole heart, we have not loved our neighbours as ourselves:
we repent, and are sorry for all our sins.
Father, forgive us.
Strengthen us to love and obey you in newness of life;
through Jesus Christ our Lord.
Amen
"""
    confessionFive = """
Lord God,
we have sinned against you;
we have done evil in your sight.
We are sorry and repent.
Have mercy on us according to your love.
Wash away our wrongdoing and cleanse us from our sin.
Renew a right spirit within us
and restore us to the joy of your salvation,
through Jesus Christ our Lord. Amen. 
"""
    return [confessionOne, confessionTwo, confessionThree, confessionFour, confessionFive][
        week].strip()


# def NextDate(day: int):
#     # 0 - 6
#     date_today = datetime.date.today()
#     date_next = date_today + datetime.timedelta((day - date_today.weekday()) % 7)
#     return date_next
@routing.GET("/dashboard/bulletin/view/index.(?:php|html?)")
@routing.GET("/dashboard/bulletin/view/?")
def bulletinView(self: BaseHandler, path):
    return self.render_jinja2("/dashboard/bulletin/view/index.html")


@routing.GET("/dashboard/bulletin/generate/index.(?:php|html?)")
@routing.GET("/dashboard/bulletin/generate/?")
def bulletinGenerate(self: BaseHandler, path):
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
        title=data[0],
        passage=data[1],
        speaker=data[2],
        outline=data[3]
    )

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
    WHERE site = ?
    """, (site,))

    # https://stackoverflow.com/questions/5891555/display-the-date-like-may-5th-using-pythons-strftime
    dateObj = datetime.strptime(date, "%Y-%m-%d")

    def suffix(d):
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')

    dateStr = dateObj.strftime('%A, {S} %B %Y').replace(
        '{S}', str(dateObj.day) + suffix(dateObj.day))

    from math import ceil
    # Should probably reorder the date from DD/MM/YYYY to YYYY/MM/DD
    data = {}
    data.update(notices=noticesSQL,
                ADDMMYYYY=dateStr,
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
                confession=getWeeklyConfession(ceil(dateObj.day / 7)), bibleReading="",
                sermonData=sermonData)
    data.update(dict(replacementsSQL))
    return self.render_jinja2("/dashboard/bulletin/bulletinTemplate.html", **data)
