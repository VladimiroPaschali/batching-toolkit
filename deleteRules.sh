#!/bin/bash
if [ $USER != "root" ]; then
    echo "You must be root to run this script"
    exit 1
fi

ETH=enp52s0f1np1

RULES=$(sudo ethtool -n $ETH | grep "Filter: " | awk '{print $NF}')


for RULE in $RULES; do
    sudo ethtool -N $ETH delete $RULE
done


