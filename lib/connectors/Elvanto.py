import functools
import urllib.parse as urllib_parse
from time import time

import tornado.auth
import tornado.escape
import tornado.httpclient
import tornado.ioloop
import tornado.web
from tornado.concurrent import future_set_result_unless_cancelled
from tornado.httpclient import HTTPRequest, AsyncHTTPClient
from tornado.httputil import HTTPServerRequest
from tornado.stack_context import wrap

from . import Database
from lib import config, auth


class Elvanto(object):
    __API_BASE_URL = "https://api.elvanto.com/v1/"
    __AUTH_DATA = ""

    class __section:
        __parent = None

        @property
        def parent(self):
            return self.__parent

        def __init__(self, parent):
            self.__parent = parent

    class people(__section):
        # https://www.elvanto.com/api/people/
        # https://www.elvanto.com/api/people-fields/#optional_fields

        async def currentUser(self):
            return await self.parent._POST("people/currentUser")

    @staticmethod
    def prepareRequest(url) -> HTTPRequest:
        pass

    def __init__(self, *, access_token=None, api_key=None):
        if access_token:
            self.__AUTH_DATA = "Bearer " + access_token
        elif api_key:
            self.__AUTH_DATA = "Basic " + api_key

        self.people = self.people(self)

    async def __fetch(self, endpoint, method, **kwargs):
        http_client = AsyncHTTPClient()

        try:
            response = await http_client.fetch(
                self.__API_BASE_URL + endpoint + ".json",
                method=method,
                headers={
                    "Authorization": self.__AUTH_DATA
                },
                **kwargs)
        except Exception as err:
            print(err)
            raise err
        else:
            return tornado.escape.json_decode(response.body)

    async def _GET(self, endpoint):
        return await self.__fetch(endpoint, method="GET")

    async def _POST(self, endpoint, post_args=None):
        if post_args is None:
            post_args = {}
        return await self.__fetch(endpoint, method="POST", body=urllib_parse.urlencode(post_args))


class ElvantoAuth(tornado.web.RequestHandler, tornado.auth.OAuth2Mixin):
    _OAUTH_AUTHORIZE_URL = "https://api.elvanto.com/oauth"
    _OAUTH_ACCESS_TOKEN_URL = "https://api.elvanto.com/oauth/token"

    @tornado.auth._auth_return_future
    def get_authenticated_user(self, code=None, client_id=None, client_secret=None, redirect_uri=None,
                               callback=None):

        http = self.get_auth_http_client()
        body = urllib_parse.urlencode({
            "redirect_uri": redirect_uri,
            "code": code,
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "authorization_code",
        })

        fut = http.fetch(self._OAUTH_ACCESS_TOKEN_URL,
                         method="POST",
                         headers={
                             'Content-Type': 'application/x-www-form-urlencoded'},
                         body=body)
        fut.add_done_callback(
            wrap(functools.partial(self._on_access_token, callback)))

    def _on_access_token(self, future, response_fut):
        try:
            response = response_fut.result()
        except Exception as e:
            future.set_exception(tornado.auth.AuthError(
                'Elvanto auth error: %s' % str(e)))
            return

        res = tornado.escape.json_decode(response.body)
        future_set_result_unless_cancelled(future, res)

    async def get(self, *args, **kwargs):
        self.request: HTTPServerRequest
        if self.get_query_argument('error', False):
            print(self.get_query_argument('error_description'))
        elif self.get_query_argument('code', False):
            try:
                access = await self.get_authenticated_user(
                    client_id=config["OAUTH"]["clientid"],
                    client_secret=config["OAUTH"]["clientsecret"],
                    code=self.get_query_argument('code'),
                    redirect_uri=config["OAUTH"]["redirecturi"]
                )
            except tornado.auth.AuthError:
                return self.redirect(self.get_login_url() + "?error=code")
            access_token = access["access_token"]

            user = (await Elvanto(access_token=access_token).people.currentUser())["person"][0]

            rID = Database.fetchOne("""
                                         SELECT id
                                         FROM users 
                                         WHERE username = ? AND userType = ?
                                         """, (user["id"], auth.AUTH_TYPE.AUTH_OAUTH))
            if not rID:
                rID = Database.insert(
                    """
                    INSERT INTO 
                        users (username, userType, {}, {}, {}, {}) 
                    VALUES (?, ?, ?, ?, ?, ?)
                    """.format(
                        auth.PEM.SITE_LOGIN, auth.PEM.SITE_ADMIN, auth.PEM.NOTICE_POST,
                        auth.PEM.NOTICE_MODIFY
                    ),
                    (user["id"], auth.AUTH_TYPE.AUTH_OAUTH, 1, 0, 1, 0)
                )
            elif not Database.fetchOne("""
                                         SELECT id
                                         FROM users 
                                         WHERE id = ? AND {} = 1
                                         """.format(auth.PEM.SITE_LOGIN), rID):
                return self.redirect(self.get_login_url() + "?error=locked")

            Database.update(
                """
                UPDATE users 
                  SET firstName = ?, lastName = ?
                WHERE
                  username = ? AND userType = ?
                """,
                (user["preferred_name"] or user["firstname"], user["lastname"], user["id"],
                 auth.AUTH_TYPE.AUTH_OAUTH)
            )

            from .. import audit
            audit.log(audit.action.SITE_LOGIN, rID)

            self.set_secure_cookie("session", "|".join(
                [auth.AUTH_TYPE.AUTH_OAUTH, user["id"], str(int(time()) + 60 * 60)]))

            return self.redirect(self.get_query_argument("next", "/"))

        else:
            await self.authorize_redirect(
                redirect_uri=config["OAUTH"]["redirecturi"],
                client_id=config["OAUTH"]["clientid"],
                scope=[",".join(["ManagePeople", "ManageCalendar"])],
                extra_params={"type": "web_server"}
            )
