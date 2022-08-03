# -*- coding:utf-8 -*-
# Date: 2022-08-03 16:08:17
# Author: xiaohao@corp.netease.com
"""

"""

import os
import shutil

GAME_NAME = "main"
sCurPath = os.getcwd()
print(sCurPath)

exeDir = os.path.join(sCurPath, "exe")
if os.path.exists(exeDir):
    shutil.rmtree(exeDir)
    print("delete exe")

sCmd = "pyinstaller -F \
--workpath=%s/exe/build \
--distpath=%s/exe/dist \
--specpath=%s/exe \
--name=%s \
-pathes=%s \
%s/main.py"\
% (sCurPath, sCurPath, sCurPath, GAME_NAME, sCurPath, sCurPath)

os.system(sCmd)
