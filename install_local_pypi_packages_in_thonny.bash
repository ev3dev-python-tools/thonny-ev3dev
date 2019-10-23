
# see: /Users/harcok/Documents/projects/des/ev3/ev3dev/__INSTALL_thonny_with_packages_and_plugins_in_development.txt

# install new packages/plugins from ./pypi/
###########################################

# Note: it first installs all dependencies from /Users/harcok/Documents/IdeaProjects/thonny-ev3dev/pypi/  directory,
#       and if not found there, then it will look only at pypi server
             
    
/Applications/Thonny-3.2.1.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7 -m pip install --user \
    -f /Users/harcok/Documents/IdeaProjects/thonny-ev3dev/pypi/  ev3devlogging thonny-ev3dev ev3devrpyc 

## install plugin: thonny-ev3dev
#/Applications/Thonny-2.1.22.app/Contents/Frameworks/Python.framework/Versions/3.6/bin/python3.6 -mpip  install --target  ~/.thonny/plugins/lib/python/site-packages/ \
#    -f /Users/harcok/Documents/IdeaProjects/thonny-ev3dev/pypi/   ev3devlogging thonny-ev3dev 
## note: we install ev3dev2simulator for the simulator, but not for the simulated ev3dev2api
#
## install package: ev3devcontext
#~/.thonny/BundledPython36/bin/pip3  install -f /Users/harcok/Documents/IdeaProjects/thonny-ev3dev/pypi/ ev3devlogging ev3dev2simulator ev3devrpyc
## note: we install ev3dev2simulator not for the simulator, but for the simulated ev3dev2api
      
