
THONNY_VERSION=3.2.4
# see: /Users/harcok/Documents/projects/des/ev3/ev3dev/__INSTALL_thonny_with_packages_and_plugins_in_development.txt

# install new packages/plugins from ./pypi/
###########################################

# Note: it first installs all dependencies from /Users/harcok/Documents/IdeaProjects/thonny-ev3dev/pypi/  directory,
#       and if not found there, then it will look only at pypi server


# BRUTE FORCE SOLUTION: below forces reinstall for everything, also dependencies (which can also be new build packages)
#/Applications/Thonny-3.2.1.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7 -m pip install --user \
#  --no-cache-dir --force-reinstall -f /Users/harcok/Documents/IdeaProjects/thonny-ev3dev/pypi/  ev3devlogging thonny-ev3dev ev3devrpyc 

# install dependencies (but not force reinstall if already installed ;  reinstalling all dependencies takes long)
printf "\ninstall dependencies\n\n"
/Applications/Thonny-$THONNY_VERSION.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7 -m pip install --user \
    'arcade' 'pyobjc;sys.platform=="darwin"' 'pyyaml' 'pymunk' 'paramiko==2.6.0' 'sftpclone==1.2.2' 'rpyc==4.1.2' 
  
printf "\n\nforced reinstall of build packaged in pypi/ \n\n"
# force reinstall build packages from pypi directory, but do not reinstall dependencies (reinstalling all dependencies takes long)
#                  `-> because these are changed in development             `-> because not change in development
/Applications/Thonny-$THONNY_VERSION.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7 -m pip install --user \
  --no-cache-dir --no-deps --force-reinstall -f /Users/harcok/Documents/IdeaProjects/thonny-ev3dev/pypi/ ev3dev2simulator  ev3devcmd  ev3devlogging  ev3devrpyc  thonny-ev3dev
                                                 # `-> location of local packages

      
