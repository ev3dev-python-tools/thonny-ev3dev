# to get this script working
# 1. copy thonny/ package into this dir
# 2. softlink ev3devcmd_package/ev3devcmd.py into this directory 
# 3. softlink ev3devcontext_package/ev3devcontext.py into this directory
# and then run this python script to run/debug thonny IDE in your favourite IDE
#
# upload to pypi
#  1. in each package run:   python3 setup.py sdist --formats zip
#  2. copy all build source distribution zips into one directory ./pypi
#  3. then upload all zips with :  python3 -m twine upload --repository pypi ./pypi/*

import sys
import os
import runpy
import sftpclone
path = os.path.dirname(sys.modules[__name__].__file__)
sys.path.insert(0, path)
runpy.run_module('thonny', run_name="__main__",alter_sys=True)
