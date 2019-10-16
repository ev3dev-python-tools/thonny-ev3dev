
d=thonny-ev3dev
printf "\n$d\n----------------------\n"
cat setup.py | grep install_requires
for d in *_package
do 
    cd $d >/dev/null
    printf "\n$d\n----------------------\n"
    cat setup.py | grep install_requires
    cd - >/dev/null
done

