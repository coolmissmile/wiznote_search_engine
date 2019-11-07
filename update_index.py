#!encoding: utf-8
import sys
import os
import time
import json
import urllib
import urllib2
import json

reload(sys)
sys.setdefaultencoding('utf-8')
WEBPORT=9009
def update_one_note(indexname):
    """
        发送 http 请求, 增量构建内存索引
    """
    request_body = {
        "index": "%s" % indexname 
    }
    request_body_json = json.dumps(request_body)
    request_header = {"a":"b"}
    urlpath = "http://127.0.0.1:%s/update_index"%(WEBPORT)
    req = urllib2.Request(urlpath, data = request_body_json, headers = request_header)
    response = urllib2.urlopen(req, timeout=2)
    print response.code
    text = response.read().decode('utf-8')
    result_json = json.loads(text, encoding='utf-8')
    print result_json


if __name__ == "__main__":
    fd = open('.wordlist', "r")
    fc = fd.read()
    fd.close()
    fc = fc.split('\n')

    for i in fc:
        if i == "":
            continue
        update_one_note(i)

