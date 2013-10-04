#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ----------------------------------------
# HOW TO START
# ============
# $ python main.py [--port=<port_num>]
#
# local debug to avoid generating .pyc files
# $ python -B main.py [--port=<port_num>]
#
# http://stackoverflow.com/questions/154443/how-to-avoid-pyc-files
# http://stackoverflow.com/questions/9408366/stop-python-from-generating-pyc-files
# ----------------------------------------

# build-in, 3rd party and my modules
import os.path
import logging

import tornado.ioloop
import tornado.web
import tornado.options
from tornado.options import define, options

import home
import setting
import error


define("port", default=8888, help="run on the given port", type=int)


def set_options():
    tornado.options.parse_command_line()    # get port number
    setting.process_port = options.port
    options.log_file_prefix = os.path.join(setting.log_dir, "%s_%s.log" \
            % (setting.app_name, tornado.options.options.port, ))
    options.log_file_max_size = setting.log_file_max_size
    options.log_file_num_backups = setting.log_file_num_backups
    tornado.options.parse_command_line()    # make log settings take effect


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", home.HomeHandler),
            # 404
            # http://groups.google.com/group/python-tornado/browse_thread
            # /thread/ba923986b7a3773e/dc40faccf12e5a98
            # http://groups.google.com/group/python-tornado/browse_thread
            # /thread/0284b5d957f92b5d/f654b2ae192b2a4e
            (r".*", error.NotFoundHandler),
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


