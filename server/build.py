# -*- coding:utf-8 -*-
# Date: 2022-08-03 16:08:17
# Author: xiaohao@corp.netease.com
"""

"""

import os
import shutil
import platform

IS_WINDOWS = True if platform.system().lower() == "windows" else False
PACKNAME = "main" if IS_WINDOWS else "main.xh"

sCurPath = os.getcwd()
print(sCurPath)

sCmd = "pyinstaller -F \
--workpath=%s/exe/build \
--distpath=%s/exe/dist \
--specpath=%s/exe \
--name=%s \
-pathes=%s \
%s/main.py"\
% (sCurPath, sCurPath, sCurPath, PACKNAME, sCurPath, sCurPath)


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
file_name = PACKNAME + ".exe" if IS_WINDOWS else PACKNAME
src = "%s/exe/dist/%s" % (sCurPath, file_name)
dec = "%s/%s" % (sCurPath, file_name)
shutil.copyfile(src, dec)

rm_exe()

# 该权限
if not IS_WINDOWS:
    os.system("chmod 755 %s" % PACKNAME)
