#!/bin/bash

WORKROOT=`pwd`
while [ 1 ];
do
    # 新增和修改的笔记
    bash ${WORKROOT}/process_wiz_note.sh INCR

    # 已删除的笔记
    bash ${WORKROOT}/delete_task.sh
    sleep 60
done

