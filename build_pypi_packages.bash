\rm -rf pypi
mkdir -p pypi

d=thonny-ev3dev
printf "\n$d\n----------------------\n"
# Only build wheel because wheel is already source package which can be
# installed in all platforms, and it has requirements in metadata.
# No need to build sdist, because not needed, and has no metadata with requirements
#python3 setup.py sdist -d pypi/ --format zip
python3 setup.py bdist_wheel -d pypi/ 
# see: https://packaging.python.org/tutorials/packaging-projects/#generating-distribution-archives
# The tar.gz file is a source archive whereas the .whl file is a built distribution.
# Newer pip versions preferentially install built distributions, but will fall back to source archives if needed.
# You should always upload a source archive and provide built archives for the platforms your project is compatible with.
# https://packaging.python.org/guides/distributing-packages-using-setuptools/#wheels
#
# https://www.python.org/dev/peps/pep-0345/
#   wheels contain requires-dist metadata     https://www.python.org/dev/peps/pep-0345/#requires-dist-multiple-use
#  => source archive doesn't has this metadata file (though specified in
#  setup.py) 

for d in submodules/*
do
    # skip thonny
    if [[ "$d" == "submodules/thonny" ]]; then continue; fi

    cd $d
    printf "\n$d\n----------------------\n"
    # Only build wheel because wheel is already source package which can be
    # installed in all platforms, and it has requirements in metadata.
    # No need to build sdist, because not needed, and has no metadata with requirements
    #python3 setup.py sdist -d ../../pypi/ --format zip
    python3 setup.py bdist_wheel -d ../../pypi/ 
    cd -
done


