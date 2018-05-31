# to get this script working
# 1. copy thonny/ package into this dir
# 2. softlink ev3devcmd_package/ev3devcmd.py into this directory 
# 3. softlink ev3devcontext_package/ev3devcontext.py into this directory
# and then run this python script to run/debug thonny IDE in your favourite IDE

import sys
import os
import runpy
path = os.path.dirname(sys.modules[__name__].__file__)
#path = os.path.join(path, '..')
#print(path)
sys.path.insert(0, path)

# below doesn't work with subprocess => no time to find out why??
#
#contextpath = os.path.join(path, 'ev3devcontext_package')
##print(contextpath)
#sys.path.insert(0, contextpath)
#
#import ev3devcontext
#print(ev3devcontext.__file__)
#
#cmdpath = os.path.join(path, 'ev3devcmd_package')
##print(cmdpath)
#sys.path.insert(0, cmdpath)
#
#import ev3devcmd
#print(ev3devcmd.__file__)

runpy.run_module('thonny', run_name="__main__",alter_sys=True)
