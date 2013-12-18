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
import tornado.web
import tornado.options
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


class BaseHandler(tornado.web.RequestHandler):
    def prepare(self):
        self._start_time = time.time()
        arguments = self.request.arguments
        logging.info("uri: %s, method: %s, user: %s, arguments: %s, ip: %s" % (
                self.request.uri, self.request.method,
                self._handler_info.get("email", "not login"),
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


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", HomeHandler),
            # 404
            # http://groups.google.com/group/python-tornado/browse_thread
            # /thread/ba923986b7a3773e/dc40faccf12e5a98
            # http://groups.google.com/group/python-tornado/browse_thread
            # /thread/0284b5d957f92b5d/f654b2ae192b2a4e
            (r".*", NotFoundHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "template"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=setting.debug,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
    set_options()
    logging.info("Server is starting on port %s" % options.port)
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

