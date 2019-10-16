
# see: /Users/harcok/Documents/projects/des/ev3/ev3dev/__INSTALL_thonny_with_packages_and_plugins_in_development.txt

# install new packages/plugins from ./pypi/
###########################################

# Note: it first installs all dependencies from /Users/harcok/Documents/IdeaProjects/thonny-ev3dev/pypi/  directory,
#       and if not found there, then it will look only at pypi server
             
    

# install plugin: thonny-ev3dev
/Applications/Thonny-2.1.22.app/Contents/Frameworks/Python.framework/Versions/3.6/bin/python3.6 -mpip  install --target  ~/.thonny/plugins/lib/python/site-packages/ -f /Users/harcok/Documents/IdeaProjects/thonny-ev3dev/pypi/  ev3devlogging thonny-ev3dev 

# install package: ev3devcontext
~/.thonny/BundledPython36/bin/pip3  install -f /Users/harcok/Documents/IdeaProjects/thonny-ev3dev/pypi/ ev3devlogging ev3devcontext    
      
