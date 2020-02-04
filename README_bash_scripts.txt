


quick usage:

  bash build_and_update_installation.bash


description:
   the bash scripts allows you in either mac/linux or cygwin
   build and install the ev3dev python tools packages

scripts:

    list_dependencies_pypi_packages_in_markdown.bash
        prints dependencies of the packages we are building

    build_pypi_packages.bash
      build the packages of this project into ./pypi/ dir
  
    install_dependencies.bash
      install all the official packages from the official pypi server on which this project's packages depend on
  
    reinstall_build_pypi_packages.bash
      (re)install the packages in the pypi/ folder which are build by this project 

    build_and_update_installation.bash
        just executes the 3 following scripts in series
         1. build_pypi_packages
         2. install_dependencies.bash
         3. reinstall_build_pypi_packages.bash
     


configuration of the scripts: 
 - PYTHON  
     the python executable to be used;  if installing in the global
     site-packages directory, then the one from that python is used.
 - INSTALL_IN_SYSTEM_DIR 
     if set then packages are installed in python's global site-packages directory
     but if not set (empty) then package are installed in user-specific
     site-packages directory.

default configuration: 
  install using the system default's "python3"  in the user site-packages dir

example configurations:
- install using the system default's "python3"  in its global site-packages dir
    export PYTHON=python3
    export INSTALL_IN_SYSTEM_DIR=1   
- install using the thonny's "python3" in its global site-packages dir
    export PYTHON=/Applications/Thonny-3.2.4.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7
    export INSTALL_IN_SYSTEM_DIR=1   

helper scripts:

    cleanup_python_user_site.bash
        remove all packages in user site directory 
        note: just deletes this directory, and then they are gone for the 'pip' installer

    list_all_dependencies_plugin_as_list.bash
       
    list_dependencies_pypi_packages_as_list.bash
        list dependencies of packages we are building
        output of this command is used to generate the file 'requirements.txt'
        which is used in the 'install_dependencies.bash' script

    list_ev3devcmd_help.bash
        shows all possible help from the ev3dev script: for its main command,
        and all its subcommands

EXPLAINING WHAT THE SCRIPTS DO
==============================

into python GLOBAL site packages 
-------------------------------

install dependencies from pypi server into python GLOBAL site packages folder:

    pip3 install -r requirements.txt


force reinstall packages from pypi/ folder into python GLOBAL site packages folder:

    pip3 install --no-cache-dir --no-deps --force-reinstall -f ./pypi/ -r reinstall.txt


into python USER site packages 
-------------------------------

note: the Thonny IDE does this by default for both packages as plugins.

install dependencies from pypi server into python user site packages folder:

    pip3 install --user -r requirements.txt  
  

force reinstall packages from pypi/ folder into python user site packages folder:

    pip3 install --user --no-cache-dir --no-deps --force-reinstall -f ./pypi/ -r reinstall.txt
