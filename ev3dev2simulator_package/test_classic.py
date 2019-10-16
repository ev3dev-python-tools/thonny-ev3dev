
#ip="131.174.224.238"

import rpyc
import socket

import platform
connection=None

def importModule(modulepath):
    global connection
    if platform.node().startswith('ev3dev'):
        result=importlib.import_module(modulepath)
    else:
        #myip="131.174.224.204"
        #myip="131.174.142.142"
        myip="harcomacbookair.dynu.net"
        import rpyc
        import socket
        try:
            # connect only the first time, then reuse connection:
            if connection == None:
               connection = rpyc.classic.connect(myip) # host name or IP address of the EV3
               # note: attach connection to function importEv3 so that doesn't get garbage collected
        except socket.timeout as ex:
            raise Exception("remote control connection timed out") from None
        result = connection.modules[modulepath]      # import modulepath remotely
    return result

# BELOW WORKS, but using import loader fails loading object
ev3dev2=importModule("ev3dev2")
m=importModule("ev3dev2.sound")
s=m.Sound()
