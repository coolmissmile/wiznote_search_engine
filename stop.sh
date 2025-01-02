#!/bin/bash

ps -ef | grep "`pwd`" | grep -v grep | awk -F ' ' '{print $2}' | while read line;
do
    kill -9 $line
done


ps -ef | grep "main.py 9009" | grep -v grep | awk -F ' ' '{print $2}' | while read line; do kill -9 $line; done
ps -ef | grep "clean_log.sh" | grep -v grep | awk -F ' ' '{print $2}' | while read line; do kill -9 $line; done
ps -ef | grep "incr_update.sh" | grep -v grep | awk -F ' ' '{print $2}' | while read line; do kill -9 $line; done
