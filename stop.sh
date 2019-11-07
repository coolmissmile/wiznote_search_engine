#!/bin/bash

ps -ef | grep "`pwd`" | grep -v grep | awk -F ' ' '{print $2}' | while read line;
do
    kill -9 $line
done
