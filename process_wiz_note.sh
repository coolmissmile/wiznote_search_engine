#!/bin/bash

# 检查机器环境
if [ "$(uname)" != "Darwin" ]; then
    echo "只支持 Mac 平台" 
    exit 255
fi



WORKROOT=`pwd`

# 检查数据源
test -d ~/.wiznote || echo "没有安装为知笔记"
test -d ~/.wiznote || exit 255

# 拷贝原始文件
mkdir -p ./notes


RUNMODE=$1 
# RUNMODE="ALL" # 全量
# RUNMODE="INCR" # 增量

if [ "x${RUNMODE}" == "xINCR" ];then
    # 增量拷贝
    echo "增量拷贝笔记文件"
    rm -rf .has.newnote
    find ~/.wiznote/*/data/notes  -type f -name "{*" -mtime -1m | while read line
    do
        cp $line  ./notes/ > /dev/null 2>&1 
        touch .has.newnote
    done
    if [ ! -f .has.newnote ]; then
        exit 0
    fi
else
    # 全量拷贝
    echo "全量拷贝笔记文件"
    find ~/.wiznote/*/data/notes  -type f -name "{*" | while read line
    do
        cp $line  ./notes/ > /dev/null 2>&1 
    done
fi


# 解压文件
bash extract.sh  # 处理过的文件, 保存到 .htmllist
if [ "x${RUNMODE}" == "xALL" ];then
    sleep 3
fi

# 解析 html 生成 text, 并行执行
python ${WORKROOT}/parse.py  .htmllist  


> .mdlist && python ${WORKROOT}/find_md.py > .mdlist

# 对 markdown 内容进行分词处理
python ${WORKROOT}/wordseg.py .mdlist  

WEBPORT=9009

# 增量构建索引
if [ "x${RUNMODE}" == "xINCR" ];then
    cp .mdlist .wordlist
    sed -i '' 's#\.md$#\.word#g' .wordlist

    cat .wordlist | while read line; 
    do
        #curl -X POST -d '{"index": "'$line'"}' 127.0.0.1:${WEBPORT}/update_index
        echo $line 
    done

    python ${WORKROOT}/update_index.py
fi

ln -sf notes template
ln -sf notes static
cp default.css ./notes/


