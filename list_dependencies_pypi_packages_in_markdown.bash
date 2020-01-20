
print_requirements_for_package() {
    package_dir="$1" 
    package_name="$2"
    cd $package_dir >/dev/null
    requirements=$( grep install_requires setup.py| sed -e 's/^\s*install_requires=//' | sed -e 's/,\s*$//')
    cd - >/dev/null
    if [[ -z "$requirements" ]]
    then 
        requirements="[ ]"
    fi    
    printf "* $package_name: $requirements\n"
}    

d=thonny-ev3dev
print_requirements_for_package . "$d"
for d in *_package
do 
    package_name=${d%_package}
    print_requirements_for_package "$d" "$package_name" 
done


