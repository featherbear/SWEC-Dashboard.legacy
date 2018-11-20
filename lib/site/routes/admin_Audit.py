import sys
from time import time, clock

time = clock if sys.platform == 'win32' else time

from tornado.escape import json_encode
from tornado.web import authenticated

from ..SiteHandler import routing
from ...jinja2_integration import BaseHandler


def errorJSON(errString):
    return json_encode({'error': errString})


@routing.GET("/dashboard/admin/audit")
def auditRedirect(self: BaseHandler, path):
    return self.redirect("/" + path + "/")


@routing.GET("/dashboard/admin/audit/")
@routing.GET("/dashboard/admin/audit/index.(?:php|html?)")
@authenticated
def auditHome(self: BaseHandler, path):
    return self.render_jinja2("/dashboard/admin/audit.html", actionsJSON=actionMapJSON())


from ... import audit


class fetchIndexes:
    ID = 0
    ACTION = 1
    AUTHOR = 2
    DATA = 3
    TIME = 4
    USER_TYPE = 5
    USERNAME = 6
    FIRST_NAME = 7
    LAST_NAME = 8


@routing.GET("/dashboard/admin/audit/actions.json")
def getActions(self: BaseHandler, path):
    return self.finish(actionMapJSON())


def actionMapJSON():
    actionMap = {}
    for id in range(len(audit.action._categories)):
        actionMap[id+1] = audit.action(id+1)
        # actionMap[actionMap[id]] = id
    return json_encode(actionMap)


from tornado.escape import json_decode


@routing.POST("/dashboard/admin/audit/data.json")
def fetchMore(self: BaseHandler, path):
    # Gets rows from the present to past
    queryStart = time()

    postArgs = json_decode(self.request.body)
    start = postArgs.get("startIndex", audit.getCount())
    amount = postArgs.get("amount", 10)
    data = audit.fetch(start, amount)

    timeTaken = time() - queryStart

    result = dict(
        results=[dict(
            id=record[fetchIndexes.ID],
            name=record[fetchIndexes.USERNAME] if record[fetchIndexes.USER_TYPE] == "LOCAL" else (
                    record[fetchIndexes.FIRST_NAME] + " " + record[fetchIndexes.LAST_NAME]).strip() if record[
                                                                                                           fetchIndexes.AUTHOR] != 0 else "Admin",
            action=record[fetchIndexes.ACTION],
            author=record[fetchIndexes.AUTHOR],
            data=record[fetchIndexes.DATA],
            time=record[fetchIndexes.TIME],
        ) for record in data],
        count=len(data),
        nextRow=start - len(data),
        generated=timeTaken,
    )

    return self.finish(json_encode(result))
