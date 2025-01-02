#!/bin/bash
set -e

WORKROOT=./
cd $WORKROOT

echo "安装依赖软件包"
bash $WORKROOT/prepare.sh

echo "停止所有服务"
bash stop.sh && sleep 2
> error.log


echo "清空所有缓存数据"
rm -rf ./notes/*

echo "全量解析为知笔记"
bash ${WORKROOT}/process_wiz_note.sh  > error.log 2>&1

echo "启动查询服务"
cd $WORKROOT
WEBPORT=9009
python ${WORKROOT}/main.py ${WEBPORT} >> error.log 2>&1  &
sleep 2

echo "后台启动增量更新服务"
cd $WORKROOT
bash ${WORKROOT}/incr_update.sh >> error.log 2>&1  &  # 后台执行

bash ${WORKROOT}/clean_log.sh >/dev/null 2>&1 &


i=0
while [ $i -le 60 ]
do
	((i=i+1))
	sleep 1
	nc -w 2 -z 127.0.0.1 ${WEBPORT} && touch .start.success
	nc -w 2 -z 127.0.0.1 ${WEBPORT} && break	
done

if [ -f .start.success ]; then
	rm -rf .start.success
	echo "启动成功"
	echo "Visit: http://127.0.0.1:${WEBPORT}/"
	exit 0
fi

echo "启动失败!"
