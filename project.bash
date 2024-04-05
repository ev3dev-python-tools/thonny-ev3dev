#IMPORTANT: this file must be read by current bash using 'source' command, otherwise the current shell cannot be activated!

#define usage message
read -r -d '' USAGE << EOF
USAGE: source project.bash  setup|reactivate|clean

   setup      : setup project env from config files pyproject.toml/context.txt 
                creates requirements.txt lockfile, creates venv (if not yet exists), activates venv and syncs venv to lockfile
   reactivate : reactivates an already setup project (requires requirements.txt lockfile to exist)
                creates (if not yet exists) venv, activates venv, and syncs venv to lockfile
   clean      : cleanup project env
                deactivates project and removes .venv, but keeps requirements.txt lockfile
                Using the requirements.txt lockfile the project can be reactivated.

NOTE: run 'reactivate' when virtual environment not yet created or not actived, 
      then the environment will be created, activated and installed with the exact list of packages in requirements.txt 
      Packages installed in the environment which are not mentioned in requirements.txt are uninstalled.  
NOTE: run 'setup' when 
      - requirements.txt file not yet exists or 
      - you changed the project dependencies in pyproject.toml/context.txt or
      - you changed platform: some python packages differ in dependencies per operating system
EOF

if [[ "$1" == "setup" ]]
then
    if [[ ! -e pyproject.toml ]]
    then 
        echo "ERROR: no pyproject.toml found"
        return
    fi 
    if [[ ! -d .venv ]]
    then 
        python3 -m venv .venv
    fi                         
    source .venv/bin/activate   
    pip install -q --upgrade pip                
    pip install -q pip-tools build
    if [[ -e "context.txt" ]]
    then
        pip-compile pyproject.toml context.txt || { echo "error reading deps from pyproject.py and context.txt" ; return ; }
    else
        pip-compile pyproject.toml  || { echo "error reading deps from pyproject.py" ; return ; }
    fi      
    pip-sync
    echo ""
    echo "initialised and activated project"
    return 
fi

if [[ "$1" == "reactivate" ]]  
then  
    if [[ ! -e requirements.txt ]]
    then 
        echo "ERROR: no requirements.txt found; run 'source project.bash setup' to create it"
        return
    fi       
    if [[ ! -d .venv ]]
    then 
       python3 -m venv .venv                    
    fi
    source .venv/bin/activate
    pip install -q --upgrade pip                 
    pip install -q pip-tools build
    pip-sync                        # pip-sync uses the requirements.txt stored in the git repo.  
    
    echo ""
    echo "reactivated project"
    return
fi

if [[ "$1" == "clean" ]]  
then  
    if [[ ! -d .venv ]]
    then 
        echo "not .venv folder found: nothing to clean"
        return
    fi     
    if [[ "$VIRTUAL_ENV" == "" ]]
    then 
       echo "venv not activated"
    else     
        if [[ "$( cd "$VIRTUAL_ENV" && pwd -P )" == "$( pwd -P )/.venv" ]] 
        then 
            echo "deactivate venv"
            deactivate
        else 
            echo "venv not activated for $PWD, so do not deactivate"
        fi   
    fi     
    if [[  -e requirements.txt ]]
    then 
        echo "keep requirements.txt file"
    fi  
    CLEANUPDIR="/tmp/venv_pid$$_date$(date '+%Y%m%d_time%H%M')"
    echo "cleanup .venv by moving it to $CLEANUPDIR; moving allows restoring by moving back"
    if mv .venv "$CLEANUPDIR"
    then 
        echo "cleanup succeeded"
    else 
        echo "ERROR: cleanup failed"
    fi  
    return  
fi

# if no argument matched, then print usage message
echo "$USAGE"

