#!/bin/bash


while [ 1 ];
do
    find . -name "*.log" -size +5000k | while read line;
    do
        tail -n 1000 $line > .error.log.tmp
        echo "" > $line
        cat .error.log.tmp >> $line
        rm -rf .error.log.tmp
        rm -rf $line
    done

    sleep 60
done
