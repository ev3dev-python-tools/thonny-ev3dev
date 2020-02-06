for d in . submodules/* 
do 
    printf "\n\n$d\n--------------------------\n"
    cd $d; 
    git push; 
    cd - >/dev/null
done 
