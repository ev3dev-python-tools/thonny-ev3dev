
import os
import sys

def prependSimulatedApiToSysPath():
     scriptdir = os.path.dirname(os.path.realpath(__file__))
     simapidir = os.path.join(scriptdir,"ev3dev2api")
     sys.path.insert(0,simapidir)


prependSimulatedApiToSysPath()
