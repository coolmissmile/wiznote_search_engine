#!/bin/bash

if [ $# -ne 1 ];then
    echo "Usage:"
    echo "    $0 listen_port"
    exit -1
fi

LISTEN_PORT=$1

ls *.py *.sh | while read line
do
    if [ "change_port.sh" == $line ];then
        continue
    fi
    sed -i '' "s/WEBPORT=9009
done

echo "Web server will listen on port ${LISTEN_PORT}"
echo "run [ bash ./start.sh ] to restart service"
