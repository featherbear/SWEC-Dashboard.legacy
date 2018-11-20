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


# @routing.POST("/notices/action/get")
# @authenticated
# def getNotice(self: RequestHandler, path):
#     self.request: HTTPServerRequest
#
#     id = self.get_body_argument("id", False)
#     if id:
#         notice = notices.getNotice(id)
#         if not notice:
#             return self.finish(errorJSON("No notice with ID " + xhtml_escape(id)))
#         return self.finish(notice.json)
#     return self.send_error(400)

@routing.GET("/dashboard/notices")
def noticesRedirect(self: BaseHandler, path):
    return self.redirect(path + "/")


@routing.GET("/dashboard/notices/submit")
def noticesSubmitRedirect(self: BaseHandler, path):
    return self.redirect(path + "/")


@routing.GET("/dashboard/notices/index.(?:php|html?)")
@routing.GET("/dashboard/notices/")
@authenticated
def noticesHome(self: BaseHandler, path):
    return self.render_jinja2("/dashboard/notices/index.html")


@routing.GET("/dashboard/notices/submit/index.(?:php|html?)")
@routing.GET("/dashboard/notices/submit/")
@authenticated
def noticesSubmit(self: BaseHandler, path):
    return self.render_jinja2("/dashboard/notices/submit/index.html")


# @routing.POST("/dashboard/notices/submit")
# @authenticated
# def submitNotice(self: RequestHandler, path):
#     self.request: HTTPServerRequest
#     self.finish(str(notices.submitNotice("Hello", "Description", self.current_user.id, 0).id))


@routing.POST("/dashboard/notices/submit/?")
@authenticated
def noticesSubmit_(self: BaseHandler, path):
    if not self.current_user.userHasPermission(PEM.NOTICE_POST):
        return self.send_error(403)
    try:
        title = self.get_body_argument("title")
        description = self.get_body_argument("description")
        date = self.get_body_argument("date")
        endDate = self.get_body_argument("endDate")
        # priority = self.get_query_argument("priority")

        notice = notices.submitNotice(title,
                                      description,
                                      self.current_user.id,
                                      date,
                                      endDate,
                                      0,
                                      )
        audit.log(audit.action.NOTICE_SUBMIT,
                  notice.author, notice.id, notice.added)
    except Exception as e:
        print(e)
    finally:
        return self.redirect("/dashboard/notices/")


class fetchIndexes:
    ID = 0
    TITLE = 1
    DESCRIPTION = 2
    AUTHOR = 3
    DATE = 4
    END_DATE = 5
    PRIORITY = 6
    ADDED = 7
    APPROVED = 8
    ACTIVE = 9
    USER_TYPE = 10
    USERNAME = 11
    FIRST_NAME = 12
    LAST_NAME = 13


@routing.POST("/dashboard/notices/approve")
@authenticated
def approveNotice(self: BaseHandler, path):
    status = False
    postArgs = json_decode(self.request.body)
    id = postArgs.get('id', False)
    if id and self.current_user.userHasPermission(PEM.NOTICE_MODIFY):
        if notices.approveNotice(id):
            status = True
            audit.log(audit.action.NOTICE_APPROVE, self.current_user, id)

    return self.write(json_encode(dict(status=status)))


@routing.POST("/dashboard/notices/edit")
@authenticated
def editNotice(self: BaseHandler, path):
    status = False
    postArgs = json_decode(self.request.body)

    id = postArgs.get('id')
    data = dict(
        title=postArgs.get('title', None),
        description=postArgs.get('description', None),
        date=postArgs.get('startDate'),
        endDate=postArgs.get('endDate', None),
    )

    if any([self.current_user.userHasPermission(PEM.NOTICE_MODIFY),
            notices.getNotice(id).author == self.current_user.id]):

        if notices.editNotice(id, data):
            audit.log(audit.action.NOTICE_EDIT, self.current_user, id)
            status = True
    return self.write(json_encode(dict(status=status)))


@routing.POST("/dashboard/notices/delete")
@authenticated
def deleteNotice(self: BaseHandler, path):
    status = False
    postArgs = json_decode(self.request.body)
    id = postArgs.get('id')
    status = True
    # if any([self.current_user.userHasPermission(PEM.NOTICE_MODIFY),
    #         notices.getNotice(id).author == self.current_user.id]):
    #     if notices.deleteNotice(id):
    #         audit.log(audit.action.NOTICE_DELETE, self.current_user, id)
    #         status = True
    return self.write(json_encode(dict(status=status)))


@routing.POST("/dashboard/notices/active")
@authenticated
def activateNotice(self: BaseHandler, path):
    status = False
    postArgs = json_decode(self.request.body)
    id = postArgs.get('id')
    turnOn = postArgs.get('active')

    if self.current_user.userHasPermission(PEM.NOTICE_MODIFY):
        if notices.toggleNotice(id, turnOn):
            audit.log(
                audit.action.NOTICE_ACTIVATE if turnOn else audit.action.NOTICE_DEACTIVATE, self.current_user, id)
            status = True

    return self.write(json_encode(dict(status=status)))


@routing.POST("/dashboard/notices/data.json")
def fetchMore(self: BaseHandler, path):
    postArgs = json_decode(self.request.body)
    start = postArgs.get("startIndex", 0)
    amount = postArgs.get("amount", 50)
    queryStart = time()

    uid = self.current_user.id
    canManage = self.current_user.userHasPermission(PEM.NOTICE_MODIFY)

    data = notices.fetch(start, amount, uid=uid,
                         showPending=canManage, showInactive=canManage)

    timeTaken = time() - queryStart

    return self.finish(json_encode(dict(
        results=[dict(
            id=record[fetchIndexes.ID],
            title=record[fetchIndexes.TITLE],
            description=record[fetchIndexes.DESCRIPTION],
            author=record[fetchIndexes.AUTHOR],

            date=record[fetchIndexes.DATE],
            endDate=record[fetchIndexes.END_DATE],

            priority=record[fetchIndexes.PRIORITY],

            added=record[fetchIndexes.ADDED],
            approved=int(record[fetchIndexes.APPROVED]) == 1,
            active=int(record[fetchIndexes.ACTIVE]) == 1,
            name=record[fetchIndexes.USERNAME] if record[fetchIndexes.USER_TYPE] == "LOCAL"
                 else (record[fetchIndexes.FIRST_NAME] + " " + record[fetchIndexes.LAST_NAME]).strip()
                 if record[fetchIndexes.AUTHOR] != 0 else "Admin",
                 ) for record in data],
        count=len(data),
        generated=timeTaken,
        uid=uid,
        canManage=canManage

    )))
