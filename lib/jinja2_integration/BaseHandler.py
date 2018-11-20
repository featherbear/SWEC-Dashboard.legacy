from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from tornado.web import RequestHandler

from ..auth import User, PEM

# https://bibhasdn.com/blog/using-jinja2-as-the-template-engine-for-tornado-web-framework/
class BaseHandler(RequestHandler):
    """
    RequestHandler already has a `render()` method. I'm writing another
    method `render_jinja2()` and keeping the API almost same.
    """

    def render_jinja2(self, template_name, **kwargs):
        """
        This is for making some extra context variables available to
        the template
        """
        kwargs.update({
            'name': self.current_user.firstName if self.current_user else "",
            'isAdmin': self.current_user.userHasPermission(PEM.SITE_ADMIN)
            # 'settings': self.settings,
            # 'STATIC_URL': self.settings.get('static_url_prefix', '/static/'),
            # 'request': self.request,
            # 'xsrf_token': self.xsrf_token,
            # 'xsrf_form_html': self.xsrf_form_html,
        })
        content = self.render_template(template_name, **kwargs)
        self.write(content)

    """
    A simple class to hold methods for rendering templates.
    """

    def render_template(self, template_name, **kwargs):
        env = Environment(loader=FileSystemLoader('site/'))

        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise TemplateNotFound(template_name)
        content = template.render(kwargs)
        return content
