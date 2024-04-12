#IMPORTANT: this file must be read by current bash using 'source' command, otherwise the current shell cannot be activated!


# default lockfile
LOCKFILE="lockfile.txt"
 
 
# # deactive venv if active
# deactivate 1>/dev/null  2>/dev/null || true
  

have_python_cmd() {
    python_cmd="$1"
    $python_cmd --version 1>/dev/null  2>/dev/null
}


# default python version  is python3
have_python_cmd "python3" || { echo "ERROR: python3 is not installed" && return; } 
# normalize default python3 version on this system to format "major.minor" 
DEFAULT_PYTHONVERSION=$("python3" -c 'import sys; print(sys.version_info[0],sys.version_info[1],sep=".")')  

  
#define usage message
read -r -d '' USAGE << EOF
NAME
       source pyproject.bash - Setup the exact same Python development project anywhere.

USAGE  
       source pyproject.bash setup [-l LOCKFILE] [-p PYTHONVERSION] [-f]
       source pyproject.bash reactivate [-l LOCKFILE]
       source pyproject.bash info|activate|clean
   
DESCRIPTION   
    Effortless and quickly setup the exact same Python development project anywhere.

    A wrapper script around Python's venv and pip-tools to EASE Python project maintenance.
    Using a development's lockfile, stored in your repository, it automates setting up the
    Python virtual environment with the same python version and EXACT same dependencies at any
    location you want. 
 
    How do you use it? Easy, first setup your project with the 'setup' command. The 'setup'
    command determines the required dependencies from the config files, and then locks
    these dependencies in a lockfile, so we can easily recreate the same developer
    environment. Then at another location 'git clone' the project, and execute the
    'reactivate' command. The 'reactive' command then uses the info in the lockfile to
    reactive the project exactly the same! Using the 'info' command we can always
    easily view the current project status. And if you only want to open the project
    in a new bash shell you can just use the 'activate' command to just activate its
    sandboxed environment in the new shell.

    A more extensive tutorial is at https://github.com/harcokuppens/pyproject.bash .


COMMANDS

 setup 
    Setup project from config files pyproject.toml and context.txt(optional).

    Creates a lockfile from these config files (using pip-compile), then reactivates
    the project (see next command). 

    The setup command locks the dependencies of the project to fixed versions in the
    lockfile. This lockfile allows us to reactivate the project with the exact same
    dependencies on other development locations. The lockfile is by default
    lockfile.txt but can be changed with the -l option. This make multiple lockfiles
    for different platforms possible. If the lockfile already exists, then your are
    first asked permission to overwrite it. With the option '-f' you can force
    overwrite.

    The default python version used is python3, which on this system is python${DEFAULT_PYTHONVERSION}.
    Most systems have python3 set to a reasonable version, and is therefore a
    reasonable default choice. However if your project requires a specific python
    version, you can require this version with the -p option. If you want to use the
    same python version as in an already existing lockfile, you can use the 'info'
    command to find out which python version that lockfile uses. The 'info' command
    also lists all available python versions on the system.

    The pyproject.toml is the new standard config file to configure your python project.
    The context.txt config file is to configure your context projects dependencies
    during development. (see explanation below).

    The context.txt and the generated lockfile are only used during development.
               
  reactivate 
    Reactivates an already setup project with an existing lockfile.
    
    Creates (if not yet exists) venv with python version in lockfile, activates venv,
    and syncs venv to lockfile (using pip-sync). Syncing venv means packages listed
    in the lockfile are installed, and packages installed not listed in the lockfile
    are uninstalled. The lockfile is by default '$LOCKFILE' but a different lockfile
    can be specified with the -l option.
                           
  activate 
    Activates project in a (new) bash shell (requires venv up to date)
    
    Only activates venv in current bash shell; convenient for opening the project
    in a new bash shell. 
            
  clean
    Cleanup project virtual environment.

    Deactivates project and removes .venv, but keeps the lockfile(s). Using the
    lockfile the project can be reactivated.
            
  info 
    Show project status.

    Lists details of current venv, lockfiles and python versions.               

  help 
    Displays this documentation.



PRACTICAL USAGE

    Normally a project gets 'setup' once, after which you store the lockfile in your project
    repository. Then on each new checkout of the project you only need to 'reactivate' it
    with the stored lockfile to get the exact same development setup.

    You only need to run 'setup' again when
      - you changed the project dependencies in pyproject.toml/context.txt or 
      - you changed platform: on run 'setup' if some python packages differ in dependencies
        for the change in platform. You should then keep a specific lockfile per platform.
        You can do this by using the '-l LOCKFILE' option to specify a platform specific
        lockfile. For example for macos arm64 we could use 'lockfile.macos-arm64.txt'.
      - When you change the python version of your project. Package versions can depend on
        python version. First run 'source project.bash clean' to remove the old '.venv'
        folder. Then run the 'setup' command with the new python version in the the '-p
        PYTHONVERSION' option.
 
    Because the '.venv' folder can be recreated it should not be include in your repository.
    You can even 'clean' the project from its '.venv' folder to reduce storage space for the
    project, and recreate it using the 'reactivate' command when you want to develop in the
    project again.

  
    
CONTEXT PROJECTS
    
    Your project may have some related projects on which your project depends, or your
    project is a dependency off. We call them 'context' projects, because these are in the
    context of your project. Often during development when making changes to your project
    you may need related changes in the context projects. Using editable installs python
    allows us to also install these context projects editable in your project. Because the
    editable installs are only needed during development we do not want to configure them
    in the pyproject.toml config. The latter file is used for building a production ready
    release package with 'python -m build'. Therefore we use a separate configfile
    'context.txt' in which we configure the editable installs purely used for development.

    The convention is to git clone a context project X into the context/X/ subdir of
    your project, and the add a line '-e context/X' to the context.txt config file.
    Also the main project is added with a line '-e .' to the context.txt config file.
    Editable install of the main project is required if your project uses the
    src-layout, because otherwise python files are in the src/ subdirectory won't be
    made available on the PYTHONPATH automatically. The editable install of your main
    project solves that!

    After git cloning the main project, then git cloning of the context projects into the
    context folder must be done manually or by a custom script.  
    Then the wrapper script can do all dependencies installs, including the editable
    installs automatically for you. The editable installs are also added to the
    project's lockfile, so if we later need to reactivate the project the editable installs
    are also done again.
 
    An example project using context projects:
    
        https://github.com/ev3dev-python-tools/thonny-ev3dev
 
    The context.txt and the lockfile are only used during development. 
    For production we only need pyproject.toml.
    

ABOUT WRAPPER SCRIPT

    Why not use venv and pip-tools directly? The wrapper script saves you from many manual
    steps using these tools, where often you have to lookup in the documentation how you
    install and use these tools. The wrapper script automates these steps, and can directly
    placed in your repository for direct usage. And if you forgot something, you just run the
    script to lookup its internal documentation. Easy as that!

    This wrapper script is used only during development. In production we are more liberal in
    requiring which versions of a dependency we allow, otherwise we would get unresolvable
    conflicts with other packages requiring the same dependency. But in production we setup an
    virtual environment only containing the package you are developing. During development we
    want every dependency locked to a specific version. We first want to develop in that
    strict environment, and not be distracted by bugs caused by a different version of a
    dependency. In a later phase, when the software is more stable, we can test
    with a more liberal version dependency.

    The wrapper script requires a modern 'pyproject.toml' project configuration setup, 
    from which it can reads the projects dependencies. It also requires bash installed.
    On Windows machines you can install the required bash with 'Git for Windows' or 'WSL2'.
    
    For more details about the wrapped tools see:

      * https://docs.python.org/3/library/venv.html
      * https://pip-tools.readthedocs.io
  
EOF

PREFIX="PYPROJECT:" # extra space already in echo command specified 

# first argument is always command 
# note if CMD not matched in script then at end of script the USAGE is printed.
CMD="$1"
shift

# parse cmd 
if [[ "$CMD" != "setup" && "$CMD" != "reactivate" && "$CMD" != "activate" && "$CMD" != "clean" && "$CMD" != "info" ]]
then 
    echo "$USAGE"
    return
fi


cleanup_env() {
    CLEANUPDIR="/tmp/venv_pid$$_date$(date '+%Y%m%d_time%H%M')"
    echo "$PREFIX cleanup .venv by moving it to $CLEANUPDIR; moving allows restoring by moving back"
    if mv .venv "$CLEANUPDIR"
    then 
        echo "$PREFIX cleanup succeeded"
    else 
        echo ""
        echo "ERROR: cleanup failed"
        echo ""
    fi  
}

# parse options 
FORCE="false"
REQ_PYTHONVERSION=""
while [[ -n "$1"  ]] do
    arg="$1"
    case $arg in 
    	"-l" ) 
            if [[ "$CMD" != "setup" && "$CMD" != "reactivate" ]]
            then
                echo ""
                echo "ERROR: option -l not allowed for command $CMD"
                echo ""
                return
            fi 
            if [[ -z "$2" ]]
            then 
                echo ""
                echo "ERROR: missing value for option -l"
                echo ""
                return
            fi       
            LOCKFILE="$2"
            shift 2
    		;;
    	"-p" ) 
            if [[ "$CMD" != "setup" ]]
            then
                echo ""
                echo "ERROR: option -p not allowed for command $CMD"
                echo ""
                return
            fi 
            if [[ -z "$2" ]]
            then 
                echo ""
                echo "ERROR: missing value for option -p"
                echo ""
                return
            fi 
            REQ_PYTHONVERSION="$2"
            shift 2 
            
            # make sure python version is installed
            have_python_cmd "python$REQ_PYTHONVERSION" ||  { 
              echo "ERROR: requested python version '$REQ_PYTHONVERSION' is not installed." 
              return
            }
            # normalize python version to major.minor format
            REQ_PYTHONVERSION=$("python$REQ_PYTHONVERSION" -c 'import sys; print(sys.version_info[0],sys.version_info[1],sep=".")') 
    
            echo "REQUESTED PYTHONVERSION: $REQ_PYTHONVERSION"
    		;;    
    	"-f" ) 
            FORCE="true"
            echo "FORCE: $FORCE"
            shift
            ;;
    	"-"* ) echo "ERROR: invalid option '$arg'"
            return
            ;;   
        * ) echo "ERROR: invalid argument '$arg'"
            return
            ;;
    esac
done



if [[ "$CMD" == "setup" ]]
then
    echo "Creating LOCKFILE: $LOCKFILE"
    
    if [[ -e "$LOCKFILE" && "$FORCE" == "false" ]]
    then
        while true; do
            echo ""
            echo "Lockfile '$LOCKFILE' already exists."
            read -p "Do you want to overwrite? (y/n) " yn
            case $yn in 
            	[yY] ) echo ok, we will proceed;
            		break;;
            	[nN] ) echo exiting...;
            		return;;
            	* ) echo invalid response;;
            esac
        done
    fi        
    if [[ ! -e pyproject.toml ]]
    then 
        echo ""
        echo "ERROR: no pyproject.toml found"
        echo ""
        return
    fi
    
    
    # verify existing venv is compatible, otherwise clean it up
    if [[ -d .venv ]]
    then
        # make sure python in venv is still installed on the system   
        if have_python_cmd ".venv/bin/python" 
        then
            VENV_PYTHONVERSION=$(.venv/bin/python -c 'import sys; print(sys.version_info[0],sys.version_info[1],sep=".")')
            if [[ -n "$REQ_PYTHONVERSION" ]]
            then
                # user requested version
                if [[ "$REQ_PYTHONVERSION" == "$VENV_PYTHONVERSION" ]]
                then  
                    echo "$PREFIX reusing existing venv with python$VENV_PYTHONVERSION"        
                else
                    echo "$PREFIX cleanup and renew venv, because python version used by venv($VENV_PYTHONVERSION) does not match python version required($REQ_PYTHONVERSION)."
                    cleanup_env   
                fi
            else 
                # use default version
                if [[ "$DEFAULT_PYTHONVERSION" == "$VENV_PYTHONVERSION" ]]
                then
                    echo "$PREFIX reusing existing venv with python$VENV_PYTHONVERSION"                            
                else    
                   echo "$PREFIX cleanup and renew venv, because python version used by venv($VENV_PYTHONVERSION) does not match default python version($DEFAULT_PYTHONVERSION)."                    
                   cleanup_env   
                fi                    
            fi             
        else 
          echo "$PREFIX cleanup and renew venv, because python version used by venv is not installed anymore."
          cleanup_env
        fi
    fi

    # case we do not have a venv (anymore), create a new one 
    if [[ ! -d .venv ]]
    then          
        if [[ -n "$REQ_PYTHONVERSION" ]]
        then
            echo "$PREFIX create new venv with the requested python version $REQ_PYTHONVERSION"
            "python$REQ_PYTHONVERSION" -m venv .venv        
        else                  
            echo "$PREFIX create new venv with default python version $DEFAULT_PYTHONVERSION"
            "python$DEFAULT_PYTHONVERSION" -m venv .venv
        fi 
    fi 

    echo "$PREFIX activate venv with latest pip and pip-tools"                          
    source .venv/bin/activate   
    pip install -q --upgrade pip                
    pip install -q pip-tools build
    
    if [[ -e "context.txt" ]]
    then
        echo "$PREFIX create lockfile from dependencies in pyproject.toml and context.txt"
        pip-compile -o "$LOCKFILE" pyproject.toml context.txt  || { echo "error reading dependencies from pyproject.py and context.txt" ; return ; }
    else
        echo "$PREFIX create lockfile from dependencies in pyproject.toml"
        pip-compile -o "$LOCKFILE" pyproject.toml || { echo "error reading dependencies from pyproject.py" ; return ; }
    fi      
    echo "$PREFIX synchronize venv with lockfile"
    pip-sync "$LOCKFILE"
    ln -s -r "$LOCKFILE" .venv/piptools-lockfile
    echo ""
    echo "$PREFIX initialised and activated project"
    return 
fi

if [[ "$CMD" == "reactivate" ]]  
then  
    echo "Using LOCKFILE: $LOCKFILE"
    
    if [[ ! -e "$LOCKFILE"  ]]
    then 
        echo ""
        echo "ERROR: no lockfile '$LOCKFILE' found" 
        echo ""
        return
    fi   
       
    LOCK_PYTHONVERSION=$(grep autogenerated "$LOCKFILE" | sed 's/.*Python //')
    # make sure python in lockfile is installed on the system   
    echo "$PREFIX Found python version $LOCK_PYTHONVERSION in lockfile '$LOCKFILE'"      
    have_python_cmd "python$LOCK_PYTHONVERSION" ||  { 
      echo "ERROR: python version $LOCK_PYTHONVERSION used in lockfile '$LOCKFILE' is not installed on this system." 
      return
    } 
    

    # verify existing venv is compatible, otherwise clean it up
    if [[ -d .venv ]]
    then
        # make sure python in venv is still installed on the system   
        if have_python_cmd ".venv/bin/python" 
        then
            VENV_PYTHONVERSION=$(.venv/bin/python -c 'import sys; print(sys.version_info[0],sys.version_info[1],sep=".")')
            if [[ "$LOCK_PYTHONVERSION" == "$VENV_PYTHONVERSION" ]]
            then  
                echo "$PREFIX Compatible venv for python$LOCK_PYTHONVERSION found: reused in reactivate."        
            else
                echo "$PREFIX cleanup and renew venv, because python version used by venv($VENV_PYTHONVERSION) does not match python version in lockfile($LOCK_PYTHONVERSION)."
                cleanup_env           
            fi             
        else 
          echo "$PREFIX cleanup and renew venv, because python version used by venv is not installed anymore."
          cleanup_env
        fi
    fi

    # case we do not have a venv (anymore), create a new one 
    if [[ ! -d .venv ]]
    then          
        echo "$PREFIX create new venv with python version $LOCK_PYTHONVERSION found in lockfile '$LOCKFILE'"
       "python$LOCK_PYTHONVERSION" -m venv .venv 
    fi 

    echo "$PREFIX activate venv with latest pip and pip-tools"    
    source .venv/bin/activate
    pip install -q --upgrade pip                 
    pip install -q pip-tools build
    echo "$PREFIX synchronize venv with lockfile"
    pip-sync  "$LOCKFILE"    # pip-sync uses the $LOCKFILE stored in the git repo.  
    ln -s -r "$LOCKFILE" .venv/piptools-lockfile
    echo ""
    echo "$PREFIX reactivated project"
    return
fi

if [[ "$CMD" == "info" ]]  
then      
    
    echo ""
    
    if [[ -d .venv ]]
    then 
        if [[ "$VIRTUAL_ENV" == "" ]]
        then 
           echo "project venv: INACTIVE"
        else     
            if [[ "$( cd "$VIRTUAL_ENV" && pwd -P )" == "$( pwd -P )/.venv" ]] 
            then 
                echo "project venv: ACTIVE"
            else 
                echo "project venv: INACTIVE"
            fi   
        fi     
        
    else      
        echo "project venv: INACTIVE"
    fi 
    configfiles=$(command ls -r pyproject.toml context.txt 2>/dev/null)
    configfiles=${configfiles:-MISSING}
    echo "project config: " $configfiles
    if [[ ! -e pyproject.toml ]]
    then 
        echo "WARNING: project is not configured"
        echo "         missing REQUIRED pyproject.toml"
    fi
    
    echo ""
    
    if [[ -d .venv ]]
    then 
        echo "venv folder: yes"
    
        VENV_LOCKFILE=$(ls -l .venv/piptools-lockfile 2>/dev/null | sed 's/^.* -> ..\///')
        echo "venv synced with LOCKFILE: " ${VENV_LOCKFILE:-UNKNOWN}
        
        if have_python_cmd ".venv/bin/python" 
        then
            VENV_PYTHONVERSION=$(.venv/bin/python -c 'import sys; print(sys.version_info[0],sys.version_info[1],sep=".")')
            echo "venv PYTHON VERSION:"  $VENV_PYTHONVERSION           
        else 
            echo "PROBLEM: python version used by venv is not installed anymore."
        fi      
        
        
        if [[ "$VIRTUAL_ENV" == "" ]]
        then 
           echo "venv: NOT activated"
        else     
            if [[ "$( cd "$VIRTUAL_ENV" && pwd -P )" == "$( pwd -P )/.venv" ]] 
            then 
                echo "venv: activated"
            else 
                echo "venv: NOT activated for current project"
            fi   
        fi     
        
    else      
        echo "venv folder: no"
    fi    
    
    
    echo ""
    
    # https://www.baeldung.com/linux/compgen-command-usage
    python_versions=$(compgen -c python3 |grep '\.' |grep -v config |sed 's/python3.//' |sort -n |uniq |sed 's/^/python3./')
    printf "python versions available on this system:\n\n"
    echo "$python_versions" | sed 's/^/    /'
    
    echo ""
    
    printf "lockfiles with corresponding python versions:\n\n"
    printf "    %-60s%s\n" "LOCKFILE" "PYTHON VERSION"
    printf "    %-60s%s\n" "--------" "--------------"    
    for f in $(compgen -f lockfile)
    do 
       version=$(grep autogenerated "$f" | sed 's/.*Python //') 
       version=${version:-UNKNOWN}
       printf "    %-60s%s\n" "$f" "$version"
    done
    
    echo ""
    
    return
fi
    
if [[ "$CMD" == "activate" ]]  
then      
    if [[ ! -d .venv ]]
    then 
        echo ""
        echo "ERROR: no .venv folder found; run 'source project.bash reactivate -l $LOCKFILE' to create it"
        echo ""
        return
    fi
    source .venv/bin/activate
    VENV_PYTHONVERSION=$(python -c 'import sys; print(sys.version_info[0],sys.version_info[1],sep=".")')
    
    echo ""
    echo "$PREFIX activated project with python$VENV_PYTHONVERSION; deactivate with the 'deactivate' command"
    return
fi

if [[ "$CMD" == "clean" ]]  
then  
    if [[ ! -d .venv ]]
    then 
        echo "$PREFIX not .venv folder found: nothing to clean"
        return
    fi     
    if [[ "$VIRTUAL_ENV" == "" ]]
    then 
       echo "$PREFIX venv not activated"
    else     
        if [[ "$( cd "$VIRTUAL_ENV" && pwd -P )" == "$( pwd -P )/.venv" ]] 
        then 
            echo "$PREFIX deactivate venv"
            deactivate
        else 
            echo "$PREFIX venv not activated for $PWD, so do not deactivate"
        fi   
    fi     
    echo "$PREFIX keeping lockfile(s)" 
    cleanup_env
    return  
fi

# if no argument matched (note: $1 could already be set in shell)
echo "$USAGE" 


