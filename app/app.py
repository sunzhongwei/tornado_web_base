#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------
# HOW TO START
# ============
# $ python main.py [--port=<port_num>]
# ----------------------------------------

# build-in, 3rd party and my modules
import time
import os.path
import logging

import tornado.ioloop
import tornado.auth
import tornado.web
import tornado.options
import tornado.escape
from tornado.options import define, options

import setting


define("port", default=8888, help="run on the given port", type=int)


def set_options():
    tornado.options.parse_command_line()    # get port number
    setting.process_port = options.port
    options.logging='debug'
    options.log_to_stderr=True
    options.log_file_prefix = os.path.join(setting.log_dir, "%s_%s.log" \
            % (setting.app_name, tornado.options.options.port, ))
    options.log_file_max_size = setting.log_file_max_size
    options.log_file_num_backups = setting.log_file_num_backups
    tornado.options.parse_command_line()    # make log settings take effect


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            login_url="/auth/login",
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            static_path=os.path.join(os.path.dirname(__file__),
                "static/" + setting.app_name),
            xsrf_cookies=True,
            # uuid.uuid4().hex
            cookie_secret="f17039a3feab43da96f825fb3f7f2a47",
            google_consumer_key="anonymous",
            google_consumer_secret="anonymous",
            debug=setting.debug,
        )
        handlers = [
            (r"/", HomeHandler),
            (r"/compose", ComposeHandler),
            (r"/auth/login", AuthLoginHandler),
            (r"/auth/logout", AuthLogoutHandler),
            # in production, serve static files from Nginx
            (r"/(favicon\.ico)", tornado.web.StaticFileHandler,
             dict(path=settings['static_path'])),
            (r"/(robots\.txt)", tornado.web.StaticFileHandler,
             dict(path=settings['static_path'])),
            (r".*", NotFoundHandler),
        ]
        tornado.web.Application.__init__(self, handlers, **settings)

        # Have one global connection to the blog DB across all handlers
        #self.db = torndb.Connection(
        #    host=options.mysql_host, database=options.mysql_database,
        #    user=options.mysql_user, password=options.mysql_password)
        self.db = None


class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

    def get_current_user(self):
        '''use self.current_user to fetch user info
        '''
        user_info = self.get_secure_cookie("dmonitoring_user")
        if not user_info:
            return None
        return tornado.escape.json_decode(user_info)

    def prepare(self):
        self._start_time = time.time()
        arguments = self.request.arguments
        logging.info("uri: %s, method: %s, user: %s, arguments: %s, ip: %s" % (
                self.request.uri, self.request.method,
                self.current_user["email"],
                arguments, self.request.remote_ip))

    def on_finish(self):
        cost_time = time.time() - self._start_time
        logging.info("cost time: %0.3f" % (cost_time, ))

    # TODO: custom error handler
    #def _handle_request_exception(self, e):
    #    self.send_error(500)


class NotFoundHandler(BaseHandler):
    def get(self):
        self.set_status(404)
        self.render("404.html")


class HomeHandler(BaseHandler):
    def get(self):
        self.render("home.html")


class ComposeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.write("You are logged in!")


class AuthLoginHandler(BaseHandler, tornado.auth.GoogleMixin):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        if self.get_argument("openid.mode", None):
            user = yield self.get_authenticated_user()
            # Save the user with e.g. set_secure_cookie()
            self.set_secure_cookie("dmonitoring_user",
                    tornado.escape.json_encode(user),
                    expires_days=7)
            self.redirect(self.get_argument("next", "/"))
        else:
            yield self.authenticate_redirect()


class AuthLogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("dmonitoring_user")
        self.redirect(self.get_argument("next", "/"))


if __name__ == "__main__":
    set_options()
    logging.info("Server is starting on port %s" % options.port)
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

