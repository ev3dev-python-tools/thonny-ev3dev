
# build all development packages in ./pypi
bash build_pypi_packages.bash

# install dependencies (but not force reinstall if already installed ;  (re)installing all dependencies takes long)
bash install_dependencies_in_thonny.bash

# install or force reinstall of all development packages, and install dependencies if not yet installed 
bash reinstall_local_pypi_packages_in_thonny.bash

