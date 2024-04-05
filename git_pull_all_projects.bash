for d in . context/* 
do 
    printf "\n\n$d\n--------------------------\n"
    cd $d; 
    git pull; 
    cd - >/dev/null
done 
