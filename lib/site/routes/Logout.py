from ..SiteHandler import routing


@routing.POST("/logout/?")
@routing.GET("/logout/?")
def logout(self, path):
    self.clear_cookie("session")
    return self.redirect(self.get_login_url())