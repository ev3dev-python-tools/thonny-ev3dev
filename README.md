The thonny-ev3dev package is a plug-in which adds EV3 support for Thonny.

To correctly use the thonny-ev3dev plugin you must not use 'import ev3dev.ev3 as ev3' to import the ev3dev library, but instead you import it as:

    # get ev3dev library in current context
    import ev3devcontext
    ev3=ev3devcontext.getEV3API()
   
Then depending on the context(simulator,EV3,pc) the right library is loaded.   

For more info about the thonny-ev3dev plugin see: https://github.com/harcokuppens/thonny-ev3dev/wiki <br>
For more info about Thonny: http://thonny.org
