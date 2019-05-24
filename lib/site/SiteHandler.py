import re
from time import time

import tornado.gen
import tornado.httputil
import tornado.web

from .. import auth
from ..jinja2_integration import BaseHandler


class routing:
    _routesPOST = {}
    _routesGET = {}

    @staticmethod
    def GET(urlRegex):
        def wrapper(func):
            # print("Updating GET route", urlRegex, "->", func)
            if urlRegex in routing._routesGET:
                raise Exception("Duplicate routing pattern: " + urlRegex)
            routing._routesGET[urlRegex] = func
            return func

        return wrapper

    @staticmethod
    def POST(urlRegex):

        def wrapper(func):
            # print("Updating POST route", urlRegex, "->", func)

            if urlRegex in routing._routesPOST:
                raise Exception("Duplicate routing pattern: " + urlRegex)
            routing._routesPOST[urlRegex] = func
            return func

        return wrapper


class SiteHandler(tornado.web.StaticFileHandler, BaseHandler):
    def initialize(self, **kwargs):
        super().initialize("site/", default_filename = "index.html")

    def get_current_user(self):
        try:
            user = auth.UserSession(
                *self.get_secure_cookie("session").split(b'|'))
            user.expiry = str(int(time()) + 60 * 60)
            self.set_secure_cookie('session', str(user))
            return user
        except Exception as e:
            # print("Auth verify fail:", e)
            return False

    @tornado.gen.coroutine
    def get(self, path, **kwargs):
        for urlRegex, function in routing._routesGET.items():
            urlRoute = re.fullmatch(urlRegex, "/" + path)
            if urlRoute:
                self.compute_etag = super(
                    tornado.web.StaticFileHandler, self).compute_etag
                function(self, path, *urlRoute.groups(), **kwargs)
                return
        yield super().get(path, **kwargs)

    def post(self, path, **kwargs):
        for urlRegex, function in routing._routesPOST.items():
            if re.match("^" + urlRegex.strip("^$") + "$", "/" + path):
                return function(self, path, **kwargs)
