

#USERSITE=$(python3 -msite --user-site)
USERSITE=$(python3 -msite --user-base)
if [[ -z "$USERSITE" ]]
then
    echo "no python user site"
else
    echo "cleaning: $USERSITE"
fi    
command rm -rf "$USERSITE"
