for d in . context/* 
do 
    printf "\n\n$d\n--------------------------\n"
    cd $d; 
    git status; 
    cd - >/dev/null
done 
