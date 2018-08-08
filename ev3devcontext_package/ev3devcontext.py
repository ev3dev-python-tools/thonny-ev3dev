import sys
import os
import platform


import importlib

connection=None

def importModule(modulepath):   
    global connection
    if platform.node() == 'ev3dev':
        result=importlib.import_module(modulepath)
    else:
        if os.environ.get('EV3MODE') == "remote":
            myip=os.environ.get('EV3IP')
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
        else:
            raise Exception("ev3 simulation not yet implemented")
    return result  



# logging levels: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
def getLogger(timing=False):
    import logging
    import datetime as dt

    class MyFormatter(logging.Formatter):
        converter=dt.datetime.fromtimestamp
        def formatTime(self, record, datefmt=None):
            ct = self.converter(record.created)
            if datefmt:
                s = ct.strftime(datefmt)
            else:
                t = ct.strftime("%Y-%m-%d %H:%M:%S")
                s = "%s,%03d" % (t, record.msecs)
            return s

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler() # logging.FileHandler(LOG_FILENAME,mode='w')
    handler.setLevel(logging.DEBUG)

    if timing:
        # [loglevel time] msg
        formatter = MyFormatter(fmt='[%(levelname)s %(asctime)s] %(message)s',datefmt='%H:%M:%S.%f')
    else:
        # [loglevel] msg
        formatter = logging.Formatter('[%(levelname)s] %(message)s')

    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger




