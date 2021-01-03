# -*- coding: UTF-8 -*-
import sys
import os
import time
import json
import glob
import itertools
import copy
import jieba
import urllib
import web
import search_engine as wizsearch
from string import Template
import markdown


reload(sys)
sys.setdefaultencoding('utf-8')

urls = (
    '/file/(.+)', 'somehtml',
    "/static/(.+)", 'static_file',
    '/search?', 'search',
    '/update_index', 'update_index',
    '/update_notelist', 'update_notelist',
    '/delete_index/(.+)', 'delete_index',
    '/', 'search',
)
app = web.application(urls, globals())

RUNTIME_DIR=os.getcwd()

htmlcss='''<!Doctype html>
<html>

<style type="text/css">
    a{font-size:19px}
    a{line-height:140%}
    a{margin: 17px}
    a{margin-top: 25px}
    a{font-style:bold;}
    a{
        font-family: Arial, Helvetica, sans-serif;	
        font-size: 16px;
    }
    a{color:#0066CC}
    a:link { text-decoration: none;}
    a:active { text-decoration:blink}
    a:hover { text-decoration:underline;color: #3333CC}
    a:visited { text-decoration: none;color: #333399;}

    p{font-size:14px}
    p{line-height:124%}
    p{margin: 6px}
    p{margin-left: 16px}
    p{font-style:bold;}
    p{ 
        text-decoration: none;
        color: #111729c4;
    }
    div {
        background-color: #FFFFFF	;
        width: 800px;
        border: 1.4px solid #F0F0F0;
        padding: 2px;
        padding-top:10px;
        margin: 4px;
        margin-top: 7px;
        margin-left: 44px;
    }

    div:hover {
        border: 1.4px solid #D8D8D8;
        background-color: #dee6f166;
    }

    .topstatus {
        background-color: #e2f1c95c;
    }

    .searchText {
    
        background-color: #FFFFFF	;
        width: 790px;
        border: 1.4px solid #F0F0F0;
        padding: 8px;
        margin: 10px;
        height: 24px;
        margin-left: 44px;
    }
    .seachBtnStyle {
        width: 100px;
        height:42px;
        padding: 0;
        font-size: 10px;
        background-color: #555555;
        color: white;
    }
    .seachBtnStyle:hover {
        background-color: #008CBA;
    }

</style>

<form action="/search" method="get">
<input id="searchTextID" class="searchText" autocomplete="off" placeholder="搜索内容" type="text", name="query" $INPUTVALUE>
<input id="seachBtn" class="seachBtnStyle" type="submit" value="SEARCH">
</form>

$SEARCH_STATUS
$SEARCHRESULT

</html>

'''

class update_index:
    def POST(self):
        request = json.loads(web.data())
        print request
        if "index" not in request:
            return """{"code": 404, "reason": "no input arg in request"}"""
        web.wiz_db.update_index(request["index"])
        return """{"code": 200, "reason": "SUCC"}"""

class update_notelist:
    def GET(self):
        print "update_notelist........."
        web.wiz_db.update_notelist()
        return """{"code": 200, "reason": "SUCC"}"""

class delete_index:
    def DELETE(self, notename):
        print "delete_index .........", notename
        search_note_name = "extract_%s" % (notename)
        # extract_7fffa137-579e-49db-973e-d5f282875c59
        web.wiz_db.delete_index(search_note_name)
        return """{"code": 200, "reason": "SUCC"}"""

class static_file:
    def GET(self, name):
        print name 
        return open('static/' + name).read()

class somehtml:
    def md2html(self, mdstr):
        exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite','markdown.extensions.tables','markdown.extensions.toc', 'markdown.extensions.fenced_code', 'markdown.extensions.nl2br']
        html = '''
        <html lang="zh-cn">
        <head>
        <meta content="text/html; charset=utf-8" http-equiv="content-type" />
        <link href="/static/default.css" rel="stylesheet">
        </head>
        <body>
        %s
        </body>
        </html>
        '''


        ret = markdown.markdown(mdstr, extensions = exts)
        print ret
        return html % ret

    def GET(self, name):
        if '/index.html' not in name:
            web.seeother('/static/' + name)
            return
        web.header('Content-Type','text/html; charset=utf-8', unique = True)

        ## 尝试渲染 markdown 格式文本
        mdlist = glob.glob('template/' + os.path.dirname(name) + "/*.md")
        for i in mdlist:
            md = open(i).read()
            if "__HASSSSS__IIIIIIMAGE__" in md:
                break
            if "[TOC]" in md or "```" in md:
                # 渲染 markdown
                return self.md2html(md)

        ## 返回原始 html
        return open('template/' + name).read()

class search(object):
    def return_home(self):
        global htmlcss
        web.header('Content-Type','text/html; charset=utf-8', unique=True)
        templ = Template(htmlcss)
        r = templ.substitute(SEARCH_STATUS="", SEARCHRESULT="", INPUTVALUE="")
        return r

    def return_html(self, ori_query, result):
        global htmlcss
        global RUNTIME_DIR
        web.header('Content-Type','text/html; charset=utf-8', unique=True)
        templ = Template(htmlcss)
        #one_template = """<div><a href="%s">%s</a><br> <p>%s</p> </div> """
        one_template = """<div><a href="%s">%s</a>|<a href="%s">wiz</a><br> <p>%s</p> </div> """
        result_html = ""

        result_count = 0
        for j in result:
            # /Users/freeman/xxxxx.tmp/xx/notes/extract_00a59061-8285-4618-9f3b-0f2ced5ee05f/index.html
            # 链接到本地html
            result_count += 1
            dochref = os.path.dirname(j["doc"])+"/index.html"
            dochref = dochref.replace(RUNTIME_DIR + "/notes", 'file')

            # 链接到 为知笔记
            wizhref = "wiz://open_document?guid=%s"%(j["doc"].split("extract_")[1].split("/")[0])

            #anchor = j["doc"]
            anchor = os.path.basename(j["doc"])
            anchor = anchor.replace(".md", '')

            abstract = j["abstract"]

            result_html += one_template % (dochref, anchor, wizhref, abstract)
            result_html += "\n"


        if result_count == 0:
            SEARCH_STATUS = "<div><p>没有搜索到结果</p></div>"
        else:
            timeused = time.time() - web.search_start_time
            timeused = float('%0.4f'%timeused)
            SEARCH_STATUS='''<div class="topstatus"><p>共找到 %s 条结果, 耗时 %s 秒</p></div>''' % (result_count, timeused)

        r = templ.substitute(SEARCH_STATUS=SEARCH_STATUS, SEARCHRESULT=result_html, INPUTVALUE='''value="%s" '''%ori_query.encode('utf-8'))
        return r

    def return_data(self, result):
        ## 解决返回中文乱码
        web.header('Content-Type','text/json; charset=utf-8', unique=True)
        r = ""
        for i in result:
            for j in result[i]:
                r += j["doc"] + "\n"
        return r

    def query_analyze(self, query):
        query = query.lower()
        query = query.replace("web.py", "webpy")
        return query

    def real_search(self):
        args = web.input()
        web.search_start_time = time.time()
        print "input:", web.input()
        print "webdata:", web.data()

        if "query" not in args:
            return self.return_home()

        query = args["query"]
        query = self.query_analyze(query)
        result = web.wiz_db.search(query)
        r = self.return_html(query, result)
        return r

    def GET(self):
        return self.real_search()

    def POST(self):
        return self.real_search()

if __name__ == "__main__":
    web.wiz_db = wizsearch.create_wiz_search()
    print "init succ"

    app.run()

