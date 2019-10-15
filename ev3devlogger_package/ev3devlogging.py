

# note:  Multiple calls to getLogger() with the same name will always return a reference to the same Logger object.
#       Therefore we use the name argument to get different independent loggers.

import logging

# get advanced preformatted logger which allows you to log with different levels
# supports also timing, and lets you configure a threshold for loglevels
# logging levels: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'
def getLogger(timing=False, showLevel=True, defaultThresholdLevel=logging.DEBUG,name=__name__):

    class MyFormatter(logging.Formatter):
        import datetime as dt
        converter=dt.datetime.fromtimestamp
        def formatTime(self, record, datefmt=None):
            ct = self.converter(record.created)
            if datefmt:
                s = ct.strftime(datefmt)
            else:
                t = ct.strftime("%Y-%m-%d %H:%M:%S")
                s = "%s,%03d" % (t, record.msecs)
            return s

    logger = logging.getLogger(name)
    # Sets the threshold for this logger. Logging messages which are less severe than level will be ignored;
    logger.setLevel(defaultThresholdLevel)

    # The StreamHandler class, located in the core logging package, sends logging output to streams such as sys.stdout,
    # sys.stderr or any file-like object (or, more precisely, any object which supports write() and flush() methods).
    # If stream is specified, the instance will use it for logging output; otherwise, sys.stderr will be used.
    handler = logging.StreamHandler()  # handler which outputs log message to stderr, which on the ev3dev os go the
    # errorlog file which you can fetch later

    # Sets the output threshold for this handler
    handler.setLevel(defaultThresholdLevel)

    formatPrefix=""  # basic prefix: no level and no timing
    if showLevel and not timing:
        formatPrefix='[%(levelname)s] '
    if timing and not showLevel:
        formatPrefix='[%(asctime)s] '
    if showLevel and timing:
        formatPrefix='[%(levelname)s %(asctime)s] '

    # date format = %H:%M:%S.%f  where %f is fraction of second to distinguish to timedlogs close to each other in time
    formatter = MyFormatter(fmt=formatPrefix + '%(message)s',datefmt='%H:%M:%S.%f')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger



# get basic preformatted log function with which you can log messages to textfile
#  supports also timing, but all log messages have an implicit INFO log level
def getLogFunction(timing=False,name=__name__):
    logger=getLogger(timing,showLevel=False,name=name)
    return logger.info

# predefined basic log function
log = getLogFunction(name="basiclog")
timedlog = getLogFunction(timing=True,name="timedlog")