mkdir -p pypi

d=thonny-ev3dev
printf "\n$d\n----------------------\n"
python3 setup.py sdist -d pypi/ --format zip

for d in submodules/*
do
    # skip thonny
    if [[ "$d" == "submodules/thonny" ]]; then continue; fi

    cd $d
    printf "\n$d\n----------------------\n"
    python3 setup.py sdist -d ../../pypi/ --format zip
    cd -
done


