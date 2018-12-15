from ...auth import PEM
from tornado.httputil import HTTPServerRequest
from tornado.web import RequestHandler, authenticated
from ...jinja2_integration import BaseHandler
from ..SiteHandler import routing
from ... import notices, audit

from time import time
from tornado.escape import json_encode, json_decode, xhtml_escape


def errorJSON(errString):
    return json_encode({'error': errString})


@routing.GET("/dashboard/sermon")
def sermonRedirect(self: BaseHandler, path):
    return self.redirect(path + "/")


@routing.GET("/dashboard/sermon/index.(?:php|html?)")
@routing.GET("/dashboard/sermon/")
@authenticated
def sermonHome(self: BaseHandler, path):
    return self.render_jinja2("/dashboard/sermon/index.html")


from ... import sermons, audit


@routing.POST("/dashboard/sermon/edit")
def editSermon(self: BaseHandler, path):
    result = False

    from ...auth import PEM
    if self.current_user.userHasPermission(PEM.SERMON_MANAGE):

        postArgs = json_decode(self.request.body)

        id = postArgs.get('id')

        title = postArgs.get('title')
        passage = postArgs.get('passage')
        speaker = postArgs.get('speaker')
        outline = postArgs.get('outline')
        if not id:
            date = postArgs.get('date')
            site = postArgs.get('site')
            d = sermons.createSermon(site, date, title, passage, speaker, outline)
            audit.log(audit.action.SERMON_CREATE, self.current_user, d)
            result = True
        else:
            sermons.editSermon(id, title, passage, speaker, outline)
            audit.log(audit.action.SERMON_EDIT, self.current_user, id)
            result = True

    return self.finish(json_encode(dict(status = result)))


@routing.POST("/dashboard/sermon/data.json")
def fetchMore(self: BaseHandler, path):
    # Gets rows from the present to past
    queryStart = time()

    postArgs = json_decode(self.request.body)
    start = postArgs.get("startIndex", 0)
    amount = postArgs.get("amount", 10)
    data = sermons.getSermons(start, amount)
    print(data)

    timeTaken = time() - queryStart

    result = dict(
        results = [dict(
            id = record[0],
            site = record[1],
            date = record[2],
            title = record[3],
            passage = record[4],
            speaker = record[5],
            outline = record[6]
        ) for record in data],
        count = len(data),
        nextRow = start - len(data),
        generated = timeTaken,
    )

    return self.finish(json_encode(result))
