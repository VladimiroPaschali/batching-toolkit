#!/bin/bash
if [ $USER != "root" ]; then
    echo "You must be root to run this script"
    exit 1
fi


RULES=$(sudo ethtool -n $1 | grep "Filter: " | awk '{print $NF}')


for RULE in $RULES; do
    sudo ethtool -N $1 delete $RULE
done


