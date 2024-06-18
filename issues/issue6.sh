# this is not working
echo "$( echo 1 ; false ; echo ERROR_1 )"
echo WARNING

# this is working
x="$( echo 1 ; false ; echo ERROR_2 )"
echo "$x"
