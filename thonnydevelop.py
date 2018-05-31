# copy thonny/ package into this dir
# be careful to keep thonny/shared/ev3devcontext.py
# and then run this python script to run/debug thonny IDE in your favourite IDE

import sys
import os
import runpy
path = os.path.dirname(sys.modules[__name__].__file__)
path = os.path.join(path, '..')
sys.path.insert(0, path)
runpy.run_module('thonny', run_name="__main__",alter_sys=True)
