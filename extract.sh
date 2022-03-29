#!/bin/bash
cd notes

> ../.htmllist

# 只寻找压缩文件, { 开头的是压缩文件,  extrace_{ 开头的是解压后文件
# 解压后删除压缩文件

find . -name "{*" | while read line;
do
    dstdir="extract_${line}"
    dstdir=`echo ${dstdir/{/} `
    dstdir=`echo ${dstdir/\}/} `
    dstdir=`echo ${dstdir/./} `
    dstdir=`echo ${dstdir/\//} `

    rm -rf $dstdir
    echo "./notes/${dstdir}/index.html" >> ../.htmllist
    mkdir -p $dstdir

    mv $line  $dstdir/src.tar.gz
    echo "Extract $line"
    tar -xzf $dstdir/src.tar.gz -C $dstdir

    # 解压完成, 删除压缩文件
    rm -rf $dstdir/src.tar.gz 
done


