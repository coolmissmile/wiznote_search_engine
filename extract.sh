#!/bin/bash
cd notes

> ../.htmllist
find . -name "{*" | while read line;
do
    dstdir="page_${line}"
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
    rm -rf $dstdir/src.tar.gz 
done


