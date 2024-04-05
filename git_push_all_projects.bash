for d in . context/* 
do 
    printf "\n\n$d\n--------------------------\n"
    cd $d; 
    git push; 
    cd - >/dev/null
done 
