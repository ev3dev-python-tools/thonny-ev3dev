for d in . submodules/* 
do 
    printf "\n\n$d\n--------------------------\n"
    cd $d; 
    git pull; 
    cd - >/dev/null
done 
