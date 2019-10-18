

last version with ev3devcontext 
   => last version of thonny plugin with the REMOTE start and debug button
      
  => last version had a new version of ev3devcontext which does fake the
     ev3dev api. (previous versions needed a special import function).
     
      ev3devcontext either loads 
        ev3dev2simulator  => faking the ev3dev2 api using simulator at backend
           or
        ev3devrpyc   => proxying  the ev3dev(2) api using remote proxing the ev3dev(2) on a remote ev3 brick

     both modules where new in this version, and could be imported directly,
     however the ev3devcontext library loads the right one in the right context
     -> on ev3 does not load anything but uses officlal ev3dev api
     -> on pc by default loads simulator version, and only when EV3DEV=remote
     then loads rpyc version. 
     Note: thonny sets this variable when pressing the remote run/debug button.
   
   
 => versions after this install on pc the ev3dev2simulator by default as
      ev3dev2/ in the python path  
      So simulator by default! If you want to use rpyc mode, then you
      need to load ev3devrpyc in your program!  
      => so special REMOTE start/debug buttons became obsolete!!


this version is also the last version where ev3devcmd was depending on the rpyc
library! This was needed for the stop/softreset command. 
Newer versions use ssh call to run a stop script on the ev3dev, and they don't
support the reset command anymore. (just reboot instead for these special cases)

this version also brings the new ev3devlogging library which is a simplified 
version of the logging functionaly,importing a basic log and a timedlog,   which used to come with the ev3devcontext
library  
=> the old version used the advanced logger, see the old wiki pages,
   the new one gives you the basic log (or timedlog) which are simpler and
   easier to use 
