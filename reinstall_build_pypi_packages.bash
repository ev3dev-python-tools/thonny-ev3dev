
# install new packages/plugins from ./pypi/
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

# BRUTE FORCE SOLUTION: below forces reinstall so we are sure we have the latest packages from ./pypi/ folder
printf "\n\nforced reinstall of build packaged in pypi/ \n\n"
# force reinstall build packages from pypi directory, but do not reinstall dependencies (reinstalling all dependencies takes long)
#                  `-> because these are changed in development             `-> because not change in development
$PYTHON -m pip install $USEROPTION --no-cache-dir --no-deps --force-reinstall -f pypi/ -r pypi_packages.txt
                                                                                 # `-> location of local packages

      
