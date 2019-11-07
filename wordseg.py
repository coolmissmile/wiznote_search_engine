# encoding: utf-8
import jieba
import os
import sys
import codecs

reload(sys)
sys.setdefaultencoding('utf-8')


stopword = {}
def wordseg(path):
    try:
        html = open(path, "r").read()
        html = html.replace("/", "")

        """
        seg_list = jieba.cut("我来到北京清华大学", cut_all=True)
        print("Full Mode: " + "/ ".join(seg_list))  # 全模式

        seg_list = jieba.cut(html, cut_all=False)
        print("Default Mode: " + "/ ".join(seg_list))  # 精确模式

        seg_list = jieba.cut("他来到了网易杭研大厦")  # 默认是精确模式
        print(", ".join(seg_list))

        """
        #seg_list = jieba.cut_for_search(html)  # 搜索引擎模式
        seg_list = jieba.cut(html, cut_all=False)

        tokenlist = []
        for i in seg_list:
            i = i.encode("utf-8")
            i = i.replace(" ", "")
            i = i.replace("\n", "")
            i = i.replace("\r", "")
            i = i.replace(".", "")
            i = i.replace(",", "")
            i = i.replace("`", "")
            i = i.replace("-", "")
            i = i.replace(":", "")
            if i == "":
                continue
            if i in stopword:
                continue
            tokenlist.append(i)

        dstfile = path.replace(".md", "") + ".word"
        dst = codecs.open(dstfile, 'w+', encoding='utf-8')
        print "Wrodseg ", path, dstfile, len(tokenlist)

        # dump to file
        for i in tokenlist:
            if len(i) >= 2:
                if i[0] == "\xc2" and i[1] == "\xa0": 
                    continue
            dst.write(i.lower())
            dst.write("\n")
        dst.close()
    except Exception as e:
        print "Error %s"%e


def build_stop_word():
    fd = open("./stopword")
    ln = fd.read()
    ln = ln.split("\n")
    for i in ln:
        stopword[i] = 1

if __name__ == "__main__":
    build_stop_word()
    if len(sys.argv) > 1:
        filelist = sys.argv[1]
        block = None
        if len(sys.argv) > 2:
            block = sys.argv[2]
        fd = open(filelist, "r")
        while True:
            ln = fd.readline()
            if not ln:
                break
            
            if block:
                if hash(ln) % 4 != int(block):
                    continue
            ln = ln.replace("\n", "")
            if ln == "":
                continue
            wordseg(ln)
        fd.close()



