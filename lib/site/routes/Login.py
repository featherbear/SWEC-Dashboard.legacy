from time import time

import tornado.httputil
import tornado.web

from ..SiteHandler import routing
from ... import auth
from ...auth.AuthenticateLocal import NoUserException, UserLockedException


@routing.POST("/login/?")
def post(self: tornado.web.RequestHandler, path):
    self.request: tornado.httputil.HTTPServerRequest

    # auth just for local (non-oauth) login

    username = self.get_body_argument('u', False)
    password = self.get_body_argument('p', False)

    try:
        id = auth.authenticate(username, password)
    except NoUserException:
        return self.redirect(self.get_login_url() + "?error=badauth")
    except UserLockedException:
        return self.redirect(self.get_login_url() + "?error=locked")
    else:
        from ... import audit
        audit.log(audit.action.SITE_LOGIN, id)
        self.set_secure_cookie("session", "|".join(
            [auth.AUTH_TYPE.AUTH_USER, username, str(int(time()) + 60 * 60)]))
        return self.redirect(self.get_query_argument("next", "/"))
