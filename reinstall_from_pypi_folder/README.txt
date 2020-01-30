
into python GLOBAL site packages (thonny does)
-------------------------------

install dependencies from pypi server into python GLOBAL site packages folder:

    pip3 install -r requirements.txt


force reinstall packages from pypi/ folder into python GLOBAL site packages folder:

    pip3 install --no-cache-dir --no-deps --force-reinstall -f ./pypi/ -r reinstall.txt


into python USER site packages (thonny does)
-------------------------------

install dependencies from pypi server into python user site packages folder:

    pip3 install --user -r requirements.txt  
  

force reinstall packages from pypi/ folder into python user site packages folder:

    pip3 install --user --no-cache-dir --no-deps --force-reinstall -f ./pypi/ -r reinstall.txt
