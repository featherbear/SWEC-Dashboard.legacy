from tornado.web import authenticated

from ..SiteHandler import routing
from ...jinja2_integration import BaseHandler

from tornado.escape import json_encode


def errorJSON(errString):
    return json_encode({'error': errString})


@routing.GET("/dashboard")
def dashboardRedirect(self: BaseHandler, path):
    return self.redirect(path + "/")


@routing.GET("/dashboard/index.(?:php|html?)")
@routing.GET("/dashboard/")
@authenticated
def dashboardHome(self: BaseHandler, path):
    return self.render_jinja2("/dashboard/index.html", name=self.current_user.firstName)
