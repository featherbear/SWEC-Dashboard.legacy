from ...auth import AUTH_TYPE, User
from ...connectors import Database
from ...auth import PEM
from tornado.httputil import HTTPServerRequest
from tornado.escape import json_decode
from ... import audit
from time import time
import sys

from tornado.escape import json_encode
from tornado.web import authenticated

from ..SiteHandler import routing
from ...jinja2_integration import BaseHandler


def errorJSON(errString):
    return json_encode({'error': errString})


@routing.GET("/dashboard/admin/sites")
def auditRedirect(self: BaseHandler, path):
    return self.redirect("/" + path + "/")


@routing.GET("/dashboard/admin/sites/")
@routing.GET("/dashboard/admin/sites/index.(?:php|html?)")
@authenticated
def auditHome(self: BaseHandler, path):
    return self.render_jinja2("/dashboard/admin/sites.html")


@routing.POST("/dashboard/admin/sites/edit")
def editSite(self: BaseHandler, path):
    postArgs = json_decode(self.request.body)

    response = dict(
        id=int,
        name=str,
        replacements={}
    )

    if "id" in postArgs:
        Database.update("""
                    UPDATE sites
                    SET name = ?
                    WHERE id = ?
                    """, (postArgs["name"], postArgs["id"]))

        response["id"] = postArgs["id"]
    else:
        response["id"] = Database.insert("""
        INSERT INTO sites (name)
        VALUES (?)
        """, (postArgs["name"],))

    response["name"] = postArgs["name"]

    for option in postArgs["replacements"]:
        if "id" in option:
            Database.update("""
            UPDATE sites_data
            SET key = ?, value = ?
            WHERE id = ?
            """, (option["key"], option["value"], option["id"]))

            response["replacements"][option["id"]] = option
        else:
            optionID = Database.insert("""
                INSERT INTO sites_data (site, key, value)
                VALUES (?, ?, ?)
                """, (response["id"], option["key"], option["value"]))
            response["replacements"][optionID] = dict(
                id=optionID,
                key=option["key"],
                value=option["value"]
            )

    return self.finish(json_encode(response))


@routing.POST("/dashboard/sites.json")
def getSites(self: BaseHandler, path):
    from ... import sites
    return self.finish(json_encode(sites.getSites()))


@routing.POST("/dashboard/admin/sites/data.json")
def fetchMore(self: BaseHandler, path):
    queryStart = time()

    sitesSQL = Database.fetchAll("SELECT id, name FROM sites")
    replacementsSQL = Database.fetchAll(
        "SELECT id, site, key, value FROM sites_data")

    replacements = {}
    for site in sitesSQL:
        replacements[site[0]] = list(
            map(list, filter(lambda record: record[1] == site[0], replacementsSQL)))
        for record in replacements[site[0]]:
            del record[1]

    timeTaken = time() - queryStart

    return self.finish(json_encode(dict(
        results=[dict(id=site[0],
                      name=site[1],
                      replacements=dict(
                          map(lambda option: (option[0], dict(id=option[0], key=option[1], value=option[2])),
                              replacements[site[0]]
                              )),
                      count=len(replacements[site[0]])
                      )
                 for site in sitesSQL],
        count=len(sitesSQL),
        generated=timeTaken,
    )))
