from ..SiteHandler import routing


@routing.GET("/")
def redirectToDashboard(self, path):
    return self.redirect("/dashboard", permanent=True)
