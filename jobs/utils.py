#!/usr/bin/env python
# ~*~ coding: utf-8 ~*~
# by leoiceo

import os
from opensa.settings import DATA_DIR

def list_upload_info(upload_id):
    file_info = {}
    # 文件源目录setting指定，遍历源目录
    upload_dir = "{}/upload/{}".format(DATA_DIR, upload_id)

    file_list = os.listdir(upload_dir)

    for i in file_list:
        if os.path.isfile("{}/{}".format(upload_dir, i)):
            file_info.setdefault(i, "file")
        else:
            file_info.setdefault(i, "dir")

    return file_info