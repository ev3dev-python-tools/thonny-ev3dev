import sys
import os

def getEV3API():

    if os.uname()[1] == 'ev3dev':
        import ev3dev.ev3 as ev3
    else:
        #print(os.environ.get('EV3MODE'))
        if os.environ.get('EV3MODE') == "remote":
            myip=os.environ.get('EV3IP')
            import rpyc
            getEV3API.conn = rpyc.classic.connect(myip) # host name or IP address of the EV3
            # note: attach connection to function importEv3 so that doesn't get garbage collected
            ev3 = getEV3API.conn.modules['ev3dev.ev3']      # import ev3dev.ev3 remotely
            return ev3
        else:
            raise Exception("ev3 simulation not yet implemented")
    return ev3



# 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'

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




