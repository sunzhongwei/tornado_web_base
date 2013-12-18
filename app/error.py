#!/usr/bin/env python
# -*- coding: utf-8 -*-

# build-in, 3rd party and my modules
import base


class NotFoundHandler(base.BaseHandler):
    def get(self):
        self.set_status(404)
        self.render("404.html")


if '__main__' == __name__:
    pass
