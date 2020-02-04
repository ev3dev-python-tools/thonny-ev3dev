
print_requirements_for_package() {
    package_dir="$1" 
    package_name="$2"
    cd $package_dir >/dev/null
    requirements=$( egrep -e "^\s*install_requires=" setup.py| sed -e 's/^\s*install_requires=//' | sed -e 's/,\s*$//')
    cd - >/dev/null
    if [[ -z "$requirements" ]]
    then 
        requirements="[ ]"
    fi    
    printf "# requirements $package_name\n"
    python3 -c "list=$requirements;print('\n'.join(list))" 
    printf "\n"
}    

d=thonny-ev3dev
print_requirements_for_package . "$d"
for d in submodules/*
do 
    # skip thonny
    if [[ "$d" == "submodules/thonny" ]]; then continue; fi

    package_name=${d#submodules/}
    print_requirements_for_package "${d}" "$package_name" 
done

version=`cat submodules/thonny/thonny/VERSION`
printf "# requirements thonny $version\n"
cat submodules/thonny/requirements.txt



