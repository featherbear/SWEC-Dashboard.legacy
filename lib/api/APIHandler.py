from lib.jinja2_integration.BaseHandler import BaseHandler
import tornado.httputil

class APIHandler(BaseHandler):
    def get(self, path):
        self.set_status(501);
        return self.write("Not implemented")




        self.request: tornado.httputil.HTTPServerRequest

        print("API (GET):", path)
        self.write("api")
        data = {
            'foo': 'bar'
        }

        print("Q", self.request.query_arguments)
        return self.render_jinja2('auth/register.html', **data)

    def post(self, path):
        self.set_status(501);

        return self.write("Not implemented")



        self.request: tornado.httputil.HTTPServerRequest

        print("\nSITE (POST):", self.request.headers)
        print("H", self.request.headers)
        print("B", self.request.body_arguments)
        print("Q", self.request.query_arguments)

        print("API (POST):", path)
        self.check_xsrf_cookie()
        pass
