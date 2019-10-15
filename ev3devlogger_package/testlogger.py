# print to log file, not shown on screen   (to stderr which ev3dev os puts in logfile)
from ev3devlogger import log
#from ev3devlogger import timedlog as log
log("starwars song(log)")

from ev3devlogger import timedlog

timedlog("starwars song(timedlog)")
print("starwars (print)")
log("starwars song")


from ev3devlogger import timedlog as log
log("starwars song (timedlog as log)")