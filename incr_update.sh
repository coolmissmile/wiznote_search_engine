#!/bin/bash

WORKROOT=`pwd`
while [ 1 ];
do
    bash ${WORKROOT}/process_wiz_note.sh INCR
    bash ${WORKROOT}/delete_task.sh
    sleep 60
done

