#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import os.path


# ----------------------------------------
# To modify
# ----------------------------------------
app_name = "app"
debug = True


# ----------------------------------------
# Readable things
# ----------------------------------------
K = 1024
M = 1024 * K
G = 1024 * M
cur_file_path = os.path.realpath(__file__)
cur_dir_path = os.path.dirname(cur_file_path)


# ----------------------------------------
# Production Information
# ----------------------------------------
version_id = cur_dir_path.split("/")[-1]
process_port = None     # set this value in main.py


# ----------------------------------------
# log
# ----------------------------------------
log_dir = "/data/logs/%s" % app_name
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file_max_size = 100 * M
log_file_num_backups = 10

