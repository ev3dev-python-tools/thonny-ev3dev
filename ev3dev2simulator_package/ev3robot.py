#!/usr/bin/env python3


#import ev3dev2context

import ev3devrpyc
#import ev3dev2simulator

print("start program")

#ev3devrpyc.importModule("ev3dev2")
#ev3devrpyc.importModule("ev3dev2.led")
#ev3devrpyc.importModule("ev3dev2.sound")
#ev3devrpyc.importModule("ev3dev2.motor")

from time import sleep


from ev3dev2.led import Leds

#leds= ev3dev2.led.Leds() # gives error: 'ev3dev2' is not defined 
leds= Leds()
leds.set_color("LEFT", "GREEN")
leds.set_color("RIGHT", "GREEN")

from ev3dev2.sound import Sound

mySound=Sound()
# play beep sound
mySound.beep()


# print to screen, doesn't get logged
print("starwars")

from ev3dev2.motor import LargeMotor, OUTPUT_A, OUTPUT_B, SpeedPercent, MoveTank

m = LargeMotor(OUTPUT_A)
m.on_for_rotations(SpeedPercent(75), 5)

sleep(3)

