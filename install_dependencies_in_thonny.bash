THONNY_VERSION=3.2.4
PYTHON=/Applications/Thonny-$THONNY_VERSION.app/Contents/Frameworks/Python.framework/Versions/3.7/bin/python3.7

# install dependencies from pypi servers
###########################################

# install dependencies (but not force reinstall if already installed ;  (re)installing all dependencies takes long)
printf "\ninstall dependencies\n\n"
$PYTHON -m pip install --user \
    'arcade==2.1.3' 'pyobjc;sys.platform=="darwin"' 'pyyaml' 'pymunk' 'paramiko==2.6.0' 'sftpclone==1.2.2' 'rpyc==4.1.2'