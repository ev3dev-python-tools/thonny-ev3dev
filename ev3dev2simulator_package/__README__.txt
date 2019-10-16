
overview
-------

the ev3dev simulator consists of two parts
 - the simulated ev3dev api  
     located in ev3dev2simulator/ev3dev2api/  within ev3dev2simulator package    
 - the simulator  
     located in ev3dev2simulator/ and as main file ev3dev2simulator/Simulator.py
     note: the simulator is not dependent on simulated ev3dev api in its ev3dev2api/ subdir 
           the ev3dev api had to be put somewhere in the simulator package


start simulator
---------------

   python3 .../ev3dev2simulator/Simulator.py

usage in robot code
-------------------

To load the simulated ev3dev api into your program do:

    import ev3dev2simulator
    # done on import: ev3dev2simulator.prependSimulatedApiToSysPath()

from then on "ev3dev" is the simulated ev3dev api.


