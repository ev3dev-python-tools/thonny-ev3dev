
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

 - first official release of thonny-ev3dev for thonny3 which is ready for production 
 
 ### Added
 - support for thonny3 
 - added new version of simulator which supports two types of playfields (large/small)
 - added extra configuration options for the EV3 simulator in the "options"->"EV3" tab

 ### Changed 
 - moved to new project website https://github.com/ev3dev-python-tools/thonny-ev3dev
   from the previous website https://github.com/harcokuppens/thonny-ev3dev/
 - for older tags lower then 1.0.0 look at the old website at https://github.com/harcokuppens/thonny-ev3dev/
 - during the move python libraries ev3devlogging, ev3devcmd and ev3devrpy where split up
   into separate projects at the same https://github.com/ev3dev-python-tools/ organisation website.
 
 ### Fixed   
 - improved connection with ev3devcmd library: delays after command to make dialog readable
   before automatic closing are now set in thonny-ev3dev plugin, and not ad-hoc
   in the ev3devcmd library anymore
   
## [0.39]  
 - moved from thonny2 to thonny3 
 - use an improved ev3devcmd (v0.39) library which supports new commands like mirror and cleanup 

## [0.38.1]
 - added exclusion of mirroring __pycache__ folders

## [0.38] 
 - removed ev3devcontext library; on pc use ev3dev api from simulator, on ev3
   use the official ev3dev api. 
 - If you import the ev3devrpyc library then we can still use remote steering mode. 
 - improved ev3devcmd which only uses paramiko and is not dependent on rpyc anymore
 - improved ev3devcmd uses sftpclone to mirror a whole source directory to ev3
 - mirror removes files/dirs on target which are not in source directory
 - mirror excludes files and directories in the rootdir  which names start with a '.'
   they are excluded both from mirroring as from deletion (if only at target,
   but not in sourcedir)

# [0.37] 
 - NEW: ev3dev2simulator
 - last version of thonny-ev3dev plugin which uses the ev3devcontext library
   with the three modes: rpyc, simulator, or original ev3dev
