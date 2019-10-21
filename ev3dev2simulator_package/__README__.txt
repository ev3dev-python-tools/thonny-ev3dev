
overview
-------

the ev3dev simulator consists of two parts
 - the simulated ev3dev api  
     located in ev3dev2/  on the python path  simulating the ev3dev2 api on the EV3
 - the simulator  
     located in ev3dev2simulator/ and as main file ev3dev2simulator/Simulator.py
     note: the simulator is not dependent on simulated ev3dev api in the ev3dev2/ dir



start simulator
---------------

if package
 * not extracted on python path:

     python3 .../ev3dev2simulator/Simulator.py

 * extracted on python path:

     python3 -m ev3dev2simulator.Simulator


usage in robot code
-------------------

To load the simulated ev3dev api into your program do:

    import ev3dev2simulator
    # done on import: ev3dev2simulator.prependSimulatedApiToSysPath()

from then on "ev3dev" is the simulated ev3dev api.


