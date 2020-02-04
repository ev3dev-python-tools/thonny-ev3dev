

USERSITE=$(python3 -msite --user-site)
if [[ -z "$USERSITE" ]]
then
    echo "no python user site"
else
    echo "cleaning: $USERSITE"
fi    
command rm -rf "$USERSITE"
