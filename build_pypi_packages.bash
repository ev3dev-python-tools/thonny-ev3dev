
d=thonny-ev3dev
printf "\n$d\n----------------------\n"
python3 setup.py sdist -d pypi/ --format zip
for d in *_package
do 
    cd $d 
    printf "\n$d\n----------------------\n"
    python3 setup.py sdist -d ../pypi/ --format zip
    cd -
done

