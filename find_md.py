# encoding: utf-8
import os
import sys
import glob

fd = open(".htmllist")
fc = fd.read()
fc = fc.split("\n")


for i in fc:
    p = os.path.dirname(i) + "/*.md"
    l = glob.glob(p)
    for j in l:
        print(j)
