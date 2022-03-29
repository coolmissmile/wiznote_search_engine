#!/bin/bash

# 哪些目录需要建索引
dirs='
    /Users/guojianyong/ssd/didi     
    /Users/guojianyong/Desktop
'


mkdir -p /tmp/find_file_list.result

> /tmp/find_file_list.result.tmp
> /tmp/find_file_list.result/index.html

for line in $dirs
do
    echo $line
    find $line -type f | while read line; 
    do 
       
       # <a href="http://">自测_仿真环境介绍</a>
        echo "$line </br>"; 
    done  >> /tmp/find_file_list.result.tmp 

done


# 忽略哪些文件
cat /tmp/find_file_list.result.tmp | grep -v '_files/'  \
    | grep -v '/.DS_Store'  \
    | grep -v '/code/' \
    > /tmp/find_file_list.result/index.html


TARNAME='{a9fd81cb-c0c7-41c4-8115-000000000000}'
rm -rf /tmp/${TARNAME}
cd /tmp/find_file_list.result/
tar -czvf /tmp/${TARNAME} . 
cd -

ls  /tmp/${TARNAME}

# 拷贝文件到wiz目录下
cp /tmp/${TARNAME} /Users/guojianyong/.wiznote/*/data/notes/


