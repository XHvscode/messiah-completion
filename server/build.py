# -*- coding:utf-8 -*-
# Date: 2022-08-03 16:08:17
# Author: xiaohao@corp.netease.com
"""

"""

import os
import shutil

GAME_NAME = "main.xh"
sCurPath = os.getcwd()
print(sCurPath)

sCmd = "pyinstaller -F \
--workpath=%s/exe/build \
--distpath=%s/exe/dist \
--specpath=%s/exe \
--name=%s \
-pathes=%s \
%s/main.py"\
% (sCurPath, sCurPath, sCurPath, GAME_NAME, sCurPath, sCurPath)


def rm_exe():
    exeDir = os.path.join(sCurPath, "exe")
    if os.path.exists(exeDir):
        shutil.rmtree(exeDir)
        print("delete exe")
    log_file = "pygls.log"
    if os.path.exists(log_file):
        os.remove(log_file)

rm_exe()

os.system(sCmd)

src = "%s/exe/dist/%s" % (sCurPath, GAME_NAME)
dec = "%s/%s" % (sCurPath, GAME_NAME)
shutil.copyfile(src, dec)

rm_exe()
