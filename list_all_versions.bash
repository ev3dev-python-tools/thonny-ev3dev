

print_versions_for_package() {
    package_dir="$1" 
    package_name="$2"
    cd $package_dir >/dev/null
    version=$( egrep -e "^\s*version=" setup.py| sed -e 's/^\s*setup=//' | sed -e 's/,\s*$//')
    cd - >/dev/null

    printf "$package_name\n"
    printf -- "---------------\n"
    printf "$version\n"
    for versionfile in `find $package_dir -name version.py |grep -v build`
    do 
        printf "\n$versionfile\n"
        cat $versionfile
    done    
}    
print_versions_for_package_special() {
    package_dir="$1" 
    package_name="$2"
    cd $package_dir >/dev/null
    version=$( egrep -e "^\s*version=" setup.py| sed -e 's/^\s*setup=//' | sed -e 's/,\s*$//')
    cd - >/dev/null

    printf "$package_name\n"
    printf -- "---------------\n"
    printf "$version\n"
    for versionfile in `find $package_dir -name version.py |grep -v build |grep -v submodules`
    do 
        printf "\n$versionfile\n"
        cat $versionfile
    done    
}    

d=thonny-ev3dev
print_versions_for_package_special . "$d"
for d in submodules/*
do 
    printf "\n"
    package_name=${d#submodules/}
    print_versions_for_package "${d}" "$package_name" 
    printf "\n"

done

