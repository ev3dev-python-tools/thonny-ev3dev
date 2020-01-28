
THONNY_VERSION=3.2.4
PYTHON=/Applications/Thonny-$THONNY_VERSION.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7
# see: /Users/harcok/Documents/projects/des/ev3/ev3dev/__INSTALL_thonny_with_packages_and_plugins_in_development.txt

#PYTHON=/usr/local/bin/python3

# install new packages/plugins from ./pypi/
###########################################

# BRUTE FORCE SOLUTION: below forces reinstall so we are sure we have the latest packages from ./pypi/ folder
printf "\n\nforced reinstall of build packaged in pypi/ \n\n"
# force reinstall build packages from pypi directory, but do not reinstall dependencies (reinstalling all dependencies takes long)
#                  `-> because these are changed in development             `-> because not change in development
$PYTHON -m pip install --user \
  --no-cache-dir --no-deps --force-reinstall -f /Users/harcok/Documents/IdeaProjects/thonny-ev3dev/pypi/ ev3dev2simulator  ev3devcmd  ev3devlogging  ev3devrpyc  thonny-ev3dev
                                                 # `-> location of local packages

      
