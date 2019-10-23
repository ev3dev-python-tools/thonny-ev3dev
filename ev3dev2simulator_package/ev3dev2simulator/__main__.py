


# run ev3dev2simulator package as script to run simulator
#  usage: python3 -m ev3dev2simulator
if __name__ == '__main__':  # start main by default
    import sys

    try:
        from ev3dev2simulator.Simulator import main
    except ImportError:
        ## below HACK not needed if ev3dev2simulator installed on PYTHONPATH
        import os
        script_dir = os.path.dirname(os.path.realpath(__file__))
        os.chdir(script_dir)
        ev3devsimulator_dir = os.path.dirname(script_dir)
        sys.path.insert(0,ev3devsimulator_dir)
        from ev3dev2simulator.Simulator import main

    sys.exit(main())
