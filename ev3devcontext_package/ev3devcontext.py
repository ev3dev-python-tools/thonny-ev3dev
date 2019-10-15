


import platform
import os
if not platform.node().startswith('ev3dev'):
    if os.environ.get('EV3MODE') == "remote":
        import ev3devrpyc
    else: 
        import ev3dev2simulator
        # done on import:  ev3dev2simulator.prependSimulatedApiToSysPath()
