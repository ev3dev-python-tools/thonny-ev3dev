#!/usr/bin/env python3

# imports
#------------
# import log function
from ev3devlogging import timedlog as log
# import ev3 API
from ev3dev2 import auto as ev3

# initialize
#------------
# initialize color sensor 
colorSensor = ev3.ColorSensor(ev3.INPUT_2)
# initialize left and right motor as tank combo
tankDrive = ev3.MoveTank(ev3.OUTPUT_A, ev3.OUTPUT_D)

# main loop
#-----------
log("drive forward")
SPEED_NORMAL = ev3.SpeedPercent(30)      # 30% of maximum speed
SPEED_BACKWARDS = ev3.SpeedPercent(-30)  # backward with SPEED_NORMAL
SPEED_ZERO   = ev3.SpeedPercent(0)       # speed=0
tankDrive.on(SPEED_NORMAL, SPEED_NORMAL)
while True:
    color = colorSensor.color
    if color == colorSensor.COLOR_BLACK: # hit black border line 
        log("hit border: backup and turn right")
        # stop
        tankDrive.stop()
        # drive backwards for the duration of 1 second
        tankDrive.on_for_seconds(SPEED_BACKWARDS,SPEED_BACKWARDS, 1)
        # rotate right for 1 second by only running the left motor forward (keep right motor off)
        tankDrive.on_for_seconds(SPEED_NORMAL,SPEED_ZERO, 1)
        log("drive forward")
        tankDrive.on(ev3.SpeedPercent(30), ev3.SpeedPercent(30))