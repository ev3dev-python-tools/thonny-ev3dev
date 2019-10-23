
# see: /Users/harcok/Documents/projects/des/ev3/ev3dev/__INSTALL_thonny_with_packages_and_plugins_in_development.txt

# install new packages/plugins from ./pypi/
###########################################

# Note: it first installs all dependencies from /Users/harcok/Documents/IdeaProjects/thonny-ev3dev/pypi/  directory,
#       and if not found there, then it will look only at pypi server
             
    
/Applications/Thonny-3.2.1.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7 -m pip install --user \
  --no-cache-dir  --force-reinstall -f /Users/harcok/Documents/IdeaProjects/thonny-ev3dev/pypi/  ev3devlogging thonny-ev3dev ev3devrpyc 

      
