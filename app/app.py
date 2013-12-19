#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------
# HOW TO START
# ============
# $ python main.py [--port=<port_num>]
# ----------------------------------------

# build-in, 3rd party and my modules
import time
import json
import datetime
import os.path
import logging

import tornado.ioloop
import tornado.web
import tornado.options
import tornado.escape
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.options import define, options

import setting


define("port", default=8888, help="run on the given port", type=int)


def set_options():
    tornado.options.parse_command_line()    # get port number
    setting.process_port = options.port
    options.log_file_prefix = os.path.join(setting.log_dir, "%s_%s.log" \
            % ( setting.app_name, tornado.options.options.port, ))
    options.log_file_max_size = setting.log_file_max_size
    options.log_file_num_backups = setting.log_file_num_backups
    tornado.options.parse_command_line()    # make log settings take effect


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            (r".*", NotFoundHandler),
        ]
        settings = dict(
            login_url="/login",
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            # uuid.uuid4().hex
            cookie_secret="f17039a3feab43da96f825fb3f7f2a47",
            debug=setting.debug,
        )
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
        # TODO: user info
        logging.info("uri: %s, method: %s, user: , arguments: %s, ip: %s" % (
                self.request.uri, self.request.method,
                arguments, self.request.remote_ip))

    def on_finish(self):
        cost_time = time.time() - self._start_time
        logging.info("cost time: %0.3f" % (cost_time, ))

    def _handle_request_exception(self, e):
        # TODO
        self.send_error(500)


class NotFoundHandler(BaseHandler):
    def get(self):
        self.set_status(404)
        self.render("404.html")


class HomeHandler(BaseHandler):
    def get(self):
        self.render("home.html")


class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html", err_msg = None)

    @tornado.web.asynchronous
    @gen.coroutine
    def post(self):
        email = self.get_argument("email")
        password = self.get_argument("password")
        d_token = self.get_argument("d_token")

        rsp = yield self._call_user_token_api(email, password, d_token)
        if rsp.code != 200:
            # TODO: let user retry
            raise Exception("Fail to get login api response, http code: " % (
                    rsp.code, ))

        ret = json.loads(rsp.body)

        if ret["status"]["code"] == "1":
            login_token = ret["user"]["login_token"]
            login_id = ret["user"]["login_id"]
            user = {"login_token": login_token}
            # save login_id, login_token to database
            record_scan.sfxxx_users.update({"login_token": login_token},
                    {"$set": {"email": email, "login_id": login_id,
                              "created_on": datetime.datetime.now()}},
                    upsert=True)
            self.set_secure_cookie("sfxxx_user",
                                   tornado.escape.json_encode(user))
            self.redirect("/")
            return
        else:
            self.render("login.html", err_msg = ret["status"]["message"])

    def _call_user_token_api(self, email, password, d_token):
        '''Format of response body:

        {
            "status": {
                "code": "1",
                "created_at": "2013-10-25 10:45:35",
                "message": "Action completed successful"
            },
            "user": {
                "login_id": "729450",
                "login_token": "bffc5a193ec31da6f4addef35ae7bf54"
            }
        }
        '''
        post_data = {
                "login_email": email,
                "login_password": password,
                "login_code": d_token,
                "login_remember": "yes",
                "lang": "cn",
                "format": "json",
        }
        post_data = urllib.urlencode(post_data)
        req = HTTPRequest(LOGIN_API_URL, method="POST",
                headers=setting.HEADERS, body=post_data)
        http_client = AsyncHTTPClient()
        return http_client.fetch(req)


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("dmonitoring_user")
        self.redirect(self.get_argument("next"), "/")


if __name__ == "__main__":
    set_options()
    logging.info("Server is starting on port %s" % options.port)
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

