#! encoding: utf-8
from bs4 import BeautifulSoup
import os
import sys
import traceback


reload(sys)
sys.setdefaultencoding('utf-8')

def find_from_tag(soup, tagname, default):
    content = soup.find_all(tagname, limit=10)
    for i in content:
        text = i.text.encode("utf-8")
        if ":" in text or "年" in text or "TOC" in text or "---" in text:
            continue
        if len(text) < 64 and len(text) > 6:
            title = text
            title = title.replace(" ", "_")
            title = title.replace("\xc2\xa0", "")
            title = title.replace("\n", "_")
            title = title.replace("/", "_")
            title = title.replace("#", "_")
            title = title.replace("-", "_")
            title = title.replace(">", "_")
            title = title.replace(",", "")
            title = title.replace("!", "")
            title = title.replace("<", "_")
            title = title.replace("=", "")
            title = title.replace(" ", "")
            title = title.replace("__", "_")
            title = title.replace("__", "_")
            title = title.replace("__", "_")
            if len(title) == 0:
                continue
            title = title[1:] if title[0] == "_" else title
            title = os.path.dirname(default) +"/" + title
            return title
    return None


def get_title(soup, default):
    r = find_from_tag(soup, ["title"], default)
    if r:
        return r
    r = find_from_tag(soup, ["h3", "h4", "h1", "h2", "h5"], default)
    if r:
        return r
    r = find_from_tag(soup, ["p"], default)
    if r:
        return r
    r = find_from_tag(soup, ["span"], default)
    if r:
        return r
    r = find_from_tag(soup, ["div"], default)
    if r:
        return r
    return default.replace(".html", "")

def parse_html(path):
    try:
        html = open(path, "r").read()
        soup = BeautifulSoup(html,'html.parser',from_encoding='utf-8')
        title = get_title(soup, path)

        if soup.find("html"):
            ps = soup.find_all(["h3", "h4", "h1", "h2", "h5", "title", "div", "p"])
        else:
            ps = [soup.text]
        
        dstfilename = "%s.md"%title
        dstfile = open(dstfilename, "w+")
        print "Parse HTML", path, "->", "%s.md"%title
        for i in ps:
            dstfile.write(i.text)
            dstfile.write("\n")

        ## 是否包含图片
        img = soup.find_all("img")
        for i in img:
            dstfile.write("__HASSSSS__IIIIIIMAGE__") 
            dstfile.write("\n")
        dstfile.close()
    except Exception as e:
        print "Error %s %s"%(e, path)
        exc_type, exc_value, exc_traceback_obj = sys.exc_info()
        print "exc_type: %s" % exc_type
        print "exc_value: %s" % exc_value
        #print "exc_traceback_obj: %s" % exc_traceback_obj
        traceback.print_tb(exc_traceback_obj)

def main():
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
            parse_html(ln)
        fd.close()



if __name__ == "__main__":
    """
    find ./notes/extract_*  -type f   > .filelist
    python parse.py  .filelist
    """
    try:
        main()
    except Exception as e:
        exc_type, exc_value, exc_traceback_obj = sys.exc_info()
        print "exc_type: %s" % exc_type
        print "exc_value: %s" % exc_value
        #print "exc_traceback_obj: %s" % exc_traceback_obj
        traceback.print_tb(exc_traceback_obj)
