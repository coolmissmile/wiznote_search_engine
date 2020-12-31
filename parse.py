#! encoding: utf-8
from bs4 import BeautifulSoup
import os
import sys
import traceback
import time
import html2text


reload(sys)
sys.setdefaultencoding('utf-8')

def _find_title_from_tag(soup, tagname, default):
    try:
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
                title = title.replace("-", "_")
                title = title.replace(">", "_")
                title = title.replace(",", "")
                title = title.replace("!", "")
                title = title.replace("<", "_")
                title = title.replace("=", "")
                title = title.replace("#", "")
                title = title.replace(" ", "")
                title = title.replace("__", "_")
                title = title.replace("__", "_")
                title = title.replace("__", "_")
                if len(title) == 0:
                    continue
                if title == "无标题":
                    continue
                title = title[1:] if title[0] == "_" else title
                title = os.path.dirname(default) +"/" + title
                return title
    except:
        pass
    return None

def _find_title_from_body(soup, default):
    try:
        for i in soup.body.find_all(True):
            text = i.text.encode("utf-8")
            if ":" in text or "年" in text or "TOC" in text or "---" in text:
                continue
            if len(text) < 64 and len(text) > 6:
                title = text
                title = title.replace(" ", "_")
                title = title.replace("\xc2\xa0", "")
                title = title.replace("\n", "_")
                title = title.replace("/", "_")
                title = title.replace("-", "_")
                title = title.replace(">", "_")
                title = title.replace(",", "")
                title = title.replace("!", "")
                title = title.replace("<", "_")
                title = title.replace("=", "")
                title = title.replace("#", "")
                title = title.replace(" ", "")
                title = title.replace("__", "_")
                title = title.replace("__", "_")
                title = title.replace("__", "_")
                if len(title) == 0:
                    continue
                if title == "无标题":
                    continue
                title = title[1:] if title[0] == "_" else title
                title = os.path.dirname(default) +"/" + title
                return title
    except:
        pass
    return None

def _get_title(soup, default):
    r = _find_title_from_body(soup, default)
    if r:
        return r
    r = _find_title_from_tag(soup, ["title"], default)
    if r:
        return r
    r = _find_title_from_tag(soup, ["h3", "h4", "h1", "h2", "h5"], default)
    if r:
        return r
    r = _find_title_from_tag(soup, ["p"], default)
    if r:
        return r
    """
    r = _find_title_from_tag(soup, ["span"], default)
    if r:
        return r
    r = _find_title_from_tag(soup, ["div"], default)
    if r:
        return r
    """
    return default.replace(".html", "")

def parse_html(path):
    try:
        html = open(path, "r").read()
        h2t = html2text.HTML2Text(bodywidth=0)
        h2t.inline_links = True
        h2t.ignore_links = True 
        h2t.ignore_images = True 
        h2t.single_line_break = True
        soup = BeautifulSoup(html,'html.parser',from_encoding='utf-8')
        title = _get_title(soup, path)

        """
        # 提取所有文本, 每个tag是一行
        for i in soup.body.find_all(True):
            print i.get_text()
        """
        dstfilename = "%s.md" % title
        dstfile = open(dstfilename, "w+")
        print "Parse HTML", path, "->", "%s.md"%title
        dstfile.write(h2t.handle(html))

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
