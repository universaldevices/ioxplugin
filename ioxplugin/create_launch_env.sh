#! /bin/sh

#$1 path to dev.init.sh
#$2 path to .iox_env

if [ -z $1 ] || [ -z $2 ]
then
    echo "path to dev.init.sh and .iox_env are mandatory "
    exit 1
fi

if [ ! -f $1 ]
then    
    echo "path to dev.init.sh $1 does not exist"
    exit 1
fi

val=$($1)

echo "$val" | awk '{print $2}' > $2
