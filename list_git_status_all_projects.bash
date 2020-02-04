for d in . submodules/* 
do 
    printf "\n\n$d\n--------------------------\n"
    cd $d; 
    git status; 
    cd - >/dev/null
done 
