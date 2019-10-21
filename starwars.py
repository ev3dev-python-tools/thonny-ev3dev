#!/usr/bin/env python3

print("start program")

from time import sleep

# get ev3dev library in current context
#import ev3devcontext

## legacy: for ev3dev
#ev3=ev3devcontext.importModule("ev3dev.ev3")
#mySound=ev3.Sound()

# for ev3dev2
from ev3dev2 import sound
#sound=ev3devcontext.importModule("ev3dev2.sound")
mySound=sound.Sound()

# get logger without times
import ev3devlogging
logger=ev3devlogging.getLogger(timing=False)

# all possible levels: DEBUG,INFO,WARNING,ERROR,CRITICAL
# only show log messages from level INFO or higher
import logging
logger.setLevel(logging.INFO)

## uncomment next line to disable logging
#logger.disabled=True;

logger.debug("debug msg")
logger.critical("critical msg")
logger.info("info msg")
logger.warn("warn msg")
logger.error("error msg")

# play beep sound
mySound.beep()

logger.debug("sleep")
sleep(3)


# print to screen, doesn't get logged
print("starwars")

logger.info("starwars song")

mySound.tone([
    (392, 350, 100), (392, 350, 100), (392, 350, 100), (311.1, 250, 100),
    (466.2, 25, 100), (392, 350, 100), (311.1, 250, 100), (466.2, 25, 100),
    (392, 700, 100), (587.32, 350, 100), (587.32, 350, 100),
    (587.32, 350, 100), (622.26, 250, 100), (466.2, 25, 100),
    (369.99, 350, 100), (311.1, 250, 100), (466.2, 25, 100), (392, 700, 100),
    (784, 350, 100), (392, 250, 100), (392, 25, 100), (784, 350, 100),
    (739.98, 250, 100), (698.46, 25, 100), (659.26, 25, 100),
    (622.26, 25, 100), (659.26, 50, 400), (415.3, 25, 200), (554.36, 350, 100),
    (523.25, 250, 100), (493.88, 25, 100), (466.16, 25, 100), (440, 25, 100),
    (466.16, 50, 400), (311.13, 25, 200), (369.99, 350, 100),
    (311.13, 250, 100), (392, 25, 100), (466.16, 350, 100), (392, 250, 100),
    (466.16, 25, 100), (587.32, 700, 100), (784, 350, 100), (392, 250, 100),
    (392, 25, 100), (784, 350, 100), (739.98, 250, 100), (698.46, 25, 100),
    (659.26, 25, 100), (622.26, 25, 100), (659.26, 50, 400), (415.3, 25, 200),
    (554.36, 350, 100), (523.25, 250, 100), (493.88, 25, 100),
    (466.16, 25, 100), (440, 25, 100), (466.16, 50, 400), (311.13, 25, 200),
    (392, 350, 100), (311.13, 250, 100), (466.16, 25, 100),
    (392.00, 300, 150), (311.13, 250, 100), (466.16, 25, 100), (392, 700)
])