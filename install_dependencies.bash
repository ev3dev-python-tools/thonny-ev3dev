# install dependencies from pypi servers
###########################################

if [[ -z "$PYTHON" ]]
then 
    PYTHON=python3
fi
if [[ -z "$INSTALL_IN_SYSTEM_DIR" ]]
then
   USEROPTION="--user" 
else   
   USEROPTION="" 
fi   

# install dependencies (but not force reinstall if already installed ;  (re)installing all dependencies takes long)
printf "\ninstall dependencies from official pypi servr\n\n"
$PYTHON -m pip install $USEROPTION -r requirements.txt
