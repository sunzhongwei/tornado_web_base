#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ---------------------------------------- 
# 功能描述
# 
# ---------------------------------------- 

# build-in, 3rd party and my modules
import base


class HomeHandler(base.BaseHandler):
    def get(self):
        self.render("home.html") 


if '__main__' == __name__:
    pass


