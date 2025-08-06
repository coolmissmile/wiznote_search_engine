#!encoding: utf-8
import sys
import os
import time
import json
import glob
import itertools
import copy
import jieba
import math
import logging
import traceback
import importlib
from functools import cmp_to_key

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


KEY_TERM_POS = 0
KEY_TF_INDEX = 1

def cmp_by_score(b, a):
    if a["score"] < b["score"]:
        return -1
    if  a["score"] > b["score"]:
        return 1
    return 0

def print_backtrace():
    f = sys._getframe(1)
    i = 1
    while True:
        if f is None:
            return
        print(" Frame:[%d] file:[%s] func:[%s] line:[%s]"%(i, f.f_code.co_filename, f.f_code.co_name, f.f_lineno))
        f = f.f_back
        i += 1

class WizIndex(object):
    def __init__(self):
        self._docid_name_map = {} # 正排信息
        # self._docid_name_map[docid]["doc"]
        # self._docid_name_map[docid]["attr"]

        self._index          = {} # 倒排信息, {"hash(term)": set(doc1, doc2, doc3, ...)}
        self._idf            = {}
        self._all_doc_count  = 0
        self._docname_docid  = {} # "filename": [id1, id2, id3 ]
        self._invalid_docid  = {}

        self._keyword        = set()
        self._keyword.add("c")
        self._keyword.add("go")
        self._keyword.add("c++")
        self._keyword.add("linux")
        self._keyword.add("git")
        self._keyword.add("shell")
        self._keyword.add("python")
        self._keyword.add("#")
        self._keyword.add("##")
        self._keyword.add("###")
        self._keyword.add("####")

    def update_index(self, indexname):
        # indexname = ./notes/page_7fffa137-579e-49db-973e-d5f282875c59/some_note.word
        docid, is_new_doc = self.__get_docid_by_name(indexname)
        if is_new_doc:
            self._all_doc_count += 1
        self.__build_one_page(docid, indexname)

    def update_notelist(self):
        wiz_note_set = {}
        for i in self._docname_docid:
            docbasename = i # page_f9f47a2a-c235-4c02-b9f1-ea7d1eb321d1
            docbasename = i.replace("page_", "")
            wiz_note_zip = "{%s}" % (docbasename)
            wiz_note_set[wiz_note_zip] = 1
        fp = open("./.wiz_note_set.json", "w+")
        fp.write(json.dumps(wiz_note_set))
        fp.close()

        fp = open("./.wiz_note_set.raw", "w+")
        for i in wiz_note_set:
            fp.write(i)
            fp.write("\n")
        fp.close()

    def delete_index(self, notename):
        # notename = page_7fffa137-579e-49db-973e-d5f282875c59
        if notename not in self._docname_docid:
            return
        for i in self._docname_docid[notename]:
            self._invalid_docid[i] = 1
        del self._docname_docid[notename]

    def __get_docid_by_name(self, indexname):
        is_new_doc = False
        # ./abc/uuid/index.html -> uuid -> docid
        docbasename = os.path.basename(os.path.dirname(indexname))
        # docbasename = "page_f9f47a2a-c235-4c02-b9f1-ea7d1eb321d1"

        if docbasename in self._docname_docid:
            self._invalid_docid[self._docname_docid[docbasename][-1]] = 1
        if docbasename not in self._docname_docid:
            self._docname_docid[docbasename] = []
            is_new_doc = True

        self._docname_docid[docbasename].append(len(self._docname_docid[docbasename]))
        self._docname_docid[docbasename][-1] = "%s:%s"%(docbasename, self._docname_docid[docbasename][-1])
        return self._docname_docid[docbasename][-1], is_new_doc 

    def __index_list(self):
        li = glob.glob('./notes/page_*/*.word')
        if len(li) <= 10:
            print("Warning: Need wordseg for all html") 
        return li

    def __extend_terms(self, terms):
        if terms is None:
            return []
        count = len(terms)
        i = 0
        result = {}
        while i < count - 4:
            result[terms[i+1] + terms[i]] = 1
            result[terms[i] + terms[i+1]] = 1
            if terms[i] in self._keyword: 
                result[terms[i] + terms[i+1] + terms[i+2]] = 1
                result[terms[i] + terms[i+1] + terms[i+2] +  terms[i+3]] = 1
            i += 1
        return list(result.keys())

    def __build_one_page_attr(self, filename):
        # 构建正排信息
        docname = filename.replace(".word", ".md")
        ret = "%s/%s"%(os.getcwd(), docname)
        ret = ret.replace("/./", '/')
        return ret 

    def __build_one_page_index(self, docid, filename):
        # 构建倒排
        fd = open(filename, "r")
        fc = fd.read()
        fd.close()

        terms = fc.split("\n")
        terms += self.__extend_terms(terms)

        # [query][词位置]
        # [query][TF打分]
        docattr = {} 

        try:
            ## term 列表 转换为 词频
            term_cnt = {}
            for c in terms:
                if c not in term_cnt:
                    term_cnt[c] = 0 
                term_cnt[c] += 1

            ## 倒排
            for c in term_cnt:
                cc = hash(c)
                if cc not in self._index:
                    self._index[cc] = set()
                self._index[cc].add(docid)

            # 初始化docattr
            for c in terms:
                cc = hash(c)
                if cc not in docattr:
                    docattr[cc] = {}
                    docattr[cc][KEY_TF_INDEX] = 0 
                    docattr[cc][KEY_TERM_POS] = [] 

            # 词位置
            for term_pos, c in enumerate(terms):
                cc = hash(c)
                docattr[cc][KEY_TERM_POS].append(term_pos)

            # 计算 TF
            PAGE_TERM_COUNT = 1.0*len(terms)
            K = 2.0*(1 - 0.75 + 0.75*PAGE_TERM_COUNT/300.0)
            for c in term_cnt:
                cc = hash(c)
                tf = term_cnt[c]/PAGE_TERM_COUNT
                tf = math.sqrt(tf)
                tf = ((2.0 + 1) * tf) / (K + tf)
                docattr[cc][KEY_TF_INDEX] = tf 

            # 前几个英文单词提权
            important_english = 0
            for i, c in enumerate(terms):
                cc = hash(c)
                if c.isalpha() and important_english < 10:
                    important_english += 1
                    docattr[cc][KEY_TF_INDEX] = self.__change_score(docattr[cc][KEY_TF_INDEX], len(c))
                if i > 20:
                    break

            # markdown 提权
            markdown_tiquan = 0
            for c in terms:
                cc = hash(c)
                if c == "toc":
                    markdown_tiquan = 0.2
                if markdown_tiquan:
                    docattr[cc][KEY_TF_INDEX] = self.__change_score(docattr[cc][KEY_TF_INDEX], markdown_tiquan)

            # 根据短语长度调整 tf
            for c in term_cnt:
                cc = hash(c)
                if len(c) > 5:
                    docattr[cc][KEY_TF_INDEX] = self.__change_score(docattr[cc][KEY_TF_INDEX], 0.01*len(c))

        except Exception as e:
            print(traceback.format_exc())
        return docattr

    def __build_one_page(self, docid, filename):
        if filename == "" or filename is None:
            return

        if docid not in self._docid_name_map:
            self._docid_name_map[docid] = {}
        # 构建正排信息
        self._docid_name_map[docid]["doc"] = self.__build_one_page_attr(filename) 

        # 构建倒排信息
        self._docid_name_map[docid]["attr"] = self.__build_one_page_index(docid, filename)


    def __add_score(self, score, weight):
        return score + weight

    def __change_score(self, score, weight):
        # 根据新的 weight 因子, 调整 score
        diff = 0
        w = weight
        if w == 0:
            return score
        if w > 0:
            ratio = (1.0 - score)/1.0
            ratio = ratio * score
            diff = (1.0 - score) * ratio
            w = w + 1.0

        if w < 0:
            ratio = (score)/1.0
            ratio = ratio * score
            diff = (0 - score) * ratio
            w = w - 1.0
        w = 1.0 - 1.0/w

        y = score + diff * w
        return y

    def build_index(self):
        docs = self.__index_list()
        for i in docs:
            docid, _ = self.__get_docid_by_name(i)
            self._all_doc_count += 1
            self.__build_one_page(docid, i)

    def __seek_one_term(self, term):
        # return {} -> [dockid]: {"docid":, "score":}
        termhash = hash(term)
        r = {}
        if termhash in self._index:
            for docid in self._index[termhash]:
                TF = self._docid_name_map[docid]["attr"][termhash][KEY_TF_INDEX]
                # 旧公式
                #IDF = (1.0 * self._all_doc_count)/len(self._index[termhash]) 

                # 新公式
                IDF = 1.0 + (self._all_doc_count - len(self._index[termhash]) + 0.5) / (len(self._index[termhash]) + 0.5)
                IDF = math.log(IDF, 10)
                TFIDF = 1.0 * TF * IDF 
                r[docid] = {
                    "score": TFIDF, 
                    "pos":   self._docid_name_map[docid]["attr"][termhash][KEY_TERM_POS],
                    "docid": docid
                    }
            return r 
        return {}

    def __close_weight(self, docid, poslist):
        """
        poslist is a list
        [0] -> set(pos1, pos2...)
        [1] -> set()

        return:
            a float [0, 5]
            数值越大, 意味着应该更大提权
        """
        if poslist is None: 
            return 0
        if len(poslist) == 0:
            return 0

        step = [2, 5, 10, 15, 20, 30, 40, 50, 60, 70, 100, 200, 400, 1000]
        """
        把每个 query 的命中位置对齐到不同粒度的位置
        所有 set 之间交集不为空视为最小紧密度
        """
        all_close_weight = None  # 所有 term 之间最大距离
        for curstep in step:
            normalize_sets = []
            for s in poslist:
                normalize_sets.append(set())
                for p in s:
                    mod = p % curstep 
                    lowbound = p - mod 
                    highbound = p + (curstep-mod)
                    normalize_sets[-1].add(lowbound)
                    normalize_sets[-1].add(highbound)

            ## 求所有集合交集
            and_set = None
            for s in normalize_sets:
                if and_set is None:
                    and_set = s
                    continue
                and_set = and_set & s
            if and_set and len(and_set) > 0:
                all_close_weight = curstep

            if all_close_weight:
                return (2.0)/all_close_weight

        """
        上面是全部term都比较临近
        下面是部分term临近
        """
        distance = []
        for curstep in step:
            part_close_weight = 0 
            normalize_sets = []
            for s in poslist:
                normalize_sets.append(set())
                for p in s:
                    mod = p % curstep 
                    lowbound = p - mod 
                    highbound = p + (curstep-mod)
                    normalize_sets[-1].add(lowbound)
                    normalize_sets[-1].add(highbound)

            ## 求任意集合的交集
            or_set = None
            for s in normalize_sets:
                if or_set is None:
                    or_set = s
                    continue
                if len(or_set & s) > 0:
                    part_close_weight += curstep
                    or_set = or_set | s
                else:
                    part_close_weight += 100 
                    or_set = or_set | s
            if part_close_weight > 0:
                distance.append(part_close_weight)
        distance.sort()
        if len(distance):
            return 1.5/(distance[0])
        return 0

    def __bestmatch_change_score(self, query, hitlist):
        ratio = len(query.split(' '))
        for i in hitlist:
            i["score"] = self.__add_score(i["score"], 2.0)
        return hitlist

    def __merge_term_or(self, hitmap):
        res = {} 
        for term in hitmap:
            for docid in hitmap[term]:
                if docid not in res:
                    res[docid] = {} 
                    res[docid]["score"] = 0
                    res[docid]["poslist"] = {} 
                    res[docid]["docid"] = "" 
                    res[docid]["hitterm"] = {} 
                # TF-IDF 累加
                res[docid]["score"] += hitmap[term][docid]["score"]
                # 所有term位置
                res[docid]["poslist"][term] = hitmap[term][docid]["pos"]
                # 文档id
                res[docid]["docid"] = docid 
                # 该文档命了哪些term
                res[docid]["hitterm"][term] = 1
        return list(res.values())

    def _get_term_weight(self, query_terms):
        ori_terms = {}
        for i in query_terms:
            ori_terms[i] = 1
        return ori_terms 

    def _mod_score_by_term_weight(self, query_terms, hitmap):
        return hitmap

    def _mod_score_by_term_count(self, query_terms, result_list):
        ori_terms = self._get_term_weight(query_terms)     
        fullcount = len(ori_terms)*1.0
        for i in result_list:
            # 命中term的数量
            hit_count = len(i["hitterm"])
            add_score = 1.0* hit_count
            i["score"] = self.__add_score(i["score"], add_score) 
        return result_list

    def _mod_score_by_close_weight(self, result_list):
        # 计算term之间紧密度
        for i in result_list:
            pos_list = list(i["poslist"].values())
            close_weight = self.__close_weight(i["docid"], pos_list)
            i["score"] = self.__add_score(i["score"], close_weight)
        return result_list 

    def __merge_term_and(self, hitmap):
        """
        求取每个关键词的文档 交集
        并且多个词命中的相同文档, 需要计算紧密度

        Returns:
            return a list, 
            res["score"] = 0.3
            res["poslist"] = {term: [pos1, pos2], term2:[pos3, pos4]} 
            res["docid"] = "" 
            res["hitterm"] = {term:1, term:1, term:1} 
        """

        ## 文档交集列表, 仅 docid
        and_set = None
        for term in hitmap:
            if and_set is None:
                and_set = set(hitmap[term])
                continue
            and_set = and_set & set(hitmap[term])

        # 初始化交集文档的初始score 值
        res = {} 
        for term in hitmap:
            for docid in hitmap[term]:
                if docid not in and_set:
                    continue
                if docid not in res:
                    res[docid] = {} 
                    res[docid]["score"] = 0
                    res[docid]["poslist"] = {} 
                    res[docid]["docid"] = "" 
                    res[docid]["hitterm"] = {} 
                # TF-IDF 累加
                res[docid]["score"] += hitmap[term][docid]["score"]
                # 所有term位置
                res[docid]["poslist"][term] = hitmap[term][docid]["pos"]
                # 文档id
                res[docid]["docid"] = docid 
                # 该文档命了哪些term
                res[docid]["hitterm"][term] = 1

        return list(res.values())

    def __avg_score(self, oldavg, w):
        """
        oldavg 之前的加权平均值
        w 新的因子
        """
        if w > 100000:
            w = 100000
        if oldavg < 1.0:
            return 2 + (oldavg+w)/2.0
        count = int(oldavg)
        oldavgavg = oldavg - count
        return count+1 + (oldavgavg*count + w)/(count+1)
      
    def __limit(self, hitlist, limit):
        if len(hitlist) > limit:
            return hitlist[:limit]
        return hitlist

    def __remove_invalid_doc(self, hitlist):
        r = []
        for i in hitlist:
            if i["docid"] not in self._invalid_docid:
                r.append(i)
        return r

    def __remove_mustnot(self, hitlist, notlist):
        if len(notlist) == 0:
            return hitlist
        notmap = {}
        for i in notlist:
            notmap[i["docid"]] = 1

        r = []
        for i in hitlist:
            if i["docid"] in notmap:
                continue
            r.append(i) 
        return r

    def __sort_result(self, hitlist):
        if hitlist is None:
            return []
        # sort hitlist by score
        hitlist.sort(key=cmp_to_key(cmp_by_score))
        return hitlist 

    def __trans_to_docfile(self, sort_doc_list):
        if sort_doc_list is None:
            return []
        for i in sort_doc_list:
            if i["docid"] in self._docid_name_map:
                i["doc"] = self._docid_name_map[i["docid"]]["doc"]
        return sort_doc_list 

    def __search_best_match(self, query, limit=50):
        # no word seg
        # query_result = {"score":, "pos":, "docid"}
        query_result = self.__seek_one_term(query)
        if len(query_result) == 0:
            return []

        hitlist = list(query_result.values()) 
        hitlist = self.__bestmatch_change_score(query, hitlist)
        sort_docid = self.__sort_result(hitlist)
        sort_docid = self.__limit(sort_docid, limit)
        logging.debug("best 检索结果数: %s, query: %s" % (len(sort_docid), query))
        return sort_docid

    def __search_well_match(self, query, limit=50):
        # with word seg
        # all term must hit
        query_terms = query.split(" ")
        result = {}
        for i in query_terms:
            # result[i] = {"score":, "pos":, "docid"}
            result[i] = self.__seek_one_term(i)

        # 根据term 重要性调整分数
        result = self._mod_score_by_term_weight(query_terms, result)
        # 拉链归并
        hitlist = self.__merge_term_and(result)
        # term匹配数调整权值, 匹配3个词 > 匹配2个词 > 匹配一个词
        hitlist = self._mod_score_by_term_count(query_terms, hitlist)
        # term紧密度
        hitlist = self._mod_score_by_close_weight(hitlist)
        # 排序
        sort_docid = self.__sort_result(hitlist)
        # 截断
        sort_docid = self.__limit(sort_docid, limit)
        logging.debug("well 检索结果数: %s, query: %s" % (len(sort_docid), query))
        return sort_docid 

    def __search_partmatch(self, query, limit=50):
        # with word seg
        # some term can missmatch
        query_terms = query.split(" ")
        result = {}
        for i in query_terms:
            # result[i] = {"score":, "pos":, "docid"}
            result[i] = self.__seek_one_term(i)
            if len(result[i]) == 0:
                del result[i]

        # 根据term 重要性调整分数
        result = self._mod_score_by_term_weight(query_terms, result)

        hitlist = self.__merge_term_or(result)

        # term匹配数调整权值, 匹配3个词 > 匹配2个词 > 匹配一个词
        hitlist = self._mod_score_by_term_count(query_terms, hitlist)
        # term紧密度
        hitlist = self._mod_score_by_close_weight(hitlist)
        # 排序
        sort_docid = self.__sort_result(hitlist)
        # 截断
        sort_docid = self.__limit(sort_docid, limit)
        logging.debug("part 检索结果数: %s, query: %s" % (len(sort_docid), query))
        return sort_docid 

    def __format_to(self, result, fmt):
        if fmt == "LIST":
            l = []
            matchtype = "BEST_MATCH"
            if matchtype in result:
                for i in result[matchtype]:
                    l.append(i)

            matchtype = "WELL_MATCH"
            if matchtype in result:
                for i in result[matchtype]:
                    l.append(i)

            matchtype = "PART_MATCH"
            if matchtype in result:
                for i in result[matchtype]:
                    l.append(i)
            return l
        return result

    def print_result(self, result):
        """
        args:
           result is a map
           [] -> BEST_MATCH ...
           [BEST_MATCH] is a list
           [BEST_MATCH][0] -> {"docid", "doc", "score"}
        """
        matchtype = "BEST_MATCH"
        if matchtype in result:
            for i in result[matchtype]:
                print(matchtype, i["doc"], i["docid"], i["score"])

        matchtype = "WELL_MATCH"
        if matchtype in result:
            for i in result[matchtype]:
                print(matchtype, i["doc"], i["docid"], i["score"])

        matchtype = "PART_MATCH"
        if matchtype in result:
            for i in result[matchtype]:
                print(matchtype, i["doc"], i["docid"], i["score"])

    def __filter_duplicate(self, result):
        res = {}
        exist = {}
        res["BEST_MATCH"] = []
        res["WELL_MATCH"] = []
        res["PART_MATCH"] = []

        matchtype = "BEST_MATCH"
        if matchtype in result:
            for i in result[matchtype]:
                if i["docid"] not in exist:
                    res[matchtype].append(i)
                    exist[i["docid"]] = 1

        matchtype = "WELL_MATCH"
        if matchtype in result:
            for i in result[matchtype]:
                if i["docid"] not in exist:
                    res[matchtype].append(i)
                    exist[i["docid"]] = 1

        matchtype = "PART_MATCH"
        if matchtype in result:
            for i in result[matchtype]:
                if i["docid"] not in exist:
                    res[matchtype].append(i)
                    exist[i["docid"]] = 1
        return res

    def __preprocess(self, query):
        query = query.strip()
        if query == "":
            return ""
        query = query.lower()
        query = " ".join([i for i in query.split(" ") if i])
        return query

    def __left_sentence_bound(self, pos, content):
        """
        从一个位置开始, 向左寻找句子的开头
        return
           句子开头的位置
        """
        start = pos
        stopchar = {}
        stopchar[" "] = 1
        stopchar["."] = 1
        stopchar[";"] = 1
        stopchar["\n"] = 1
        stopchar["\r"] = 1
        stopchar["。"] = 1
        stopchar["；"] = 1
        i = 0
        while start > 0:
            i += 1
            if i < 48:
                if content[start] in stopchar:
                    i -= 1
                start -= 1
                continue
            if content[start] in stopchar:
                return start + 1
            start -= 1
            if i > 300:
                if content[start] > " " and content[start] < "~":
                    break

        return start

    def __right_sentence_bound(self, pos, content):
        """
        从一个位置开始, 向右边寻找句子的结尾
        return
           句子结尾的位置
        """
        start = pos
        stopchar = {}
        stopchar[" "] = 1
        stopchar["."] = 1
        stopchar[";"] = 1
        stopchar["\n"] = 1
        stopchar["\r"] = 1
        stopchar["。"] = 1
        stopchar["；"] = 1
        i = 0
        while start < len(content):
            i += 1
            if i < 128:
                if content[start] in stopchar:
                    i -= 1
                start += 1
                continue
            if content[start] in stopchar:
                return start + 1
            start += 1
            if i > 300:
                if content[start] > " " and content[start] < "~":
                    break
        return start



    def __abstract_one_by_query(self, query, filecontent):
        fc = filecontent
        if query in fc:
            pos = fc.find(query)
            left = self.__left_sentence_bound(pos, fc) 
            right = self.__right_sentence_bound(pos, fc)
            ab = fc[left:right]
            ab = ab.replace("\n", "")
            ab = ab.replace("  ", " ")
            ab = ab.replace("  ", " ")
            ab = ab.replace("\xc2\xa0", "")
            ab = ab.replace("  ", " ")
            ab = ab.replace("\r", "")
            # 飘红
            keyred = """<span style="color:#F08080">%s</span>"""%(query)
            ab = ab.replace(query, keyred)
            ab = ab.replace("__hasssss__iiiiiimage__", "")
            return ab 
        
        tmp_query = query.replace(" ", '')
        if tmp_query in fc:
            pos = fc.find(tmp_query)
            left = self.__left_sentence_bound(pos, fc) 
            right = self.__right_sentence_bound(pos, fc)
            ab = fc[left:right]
            ab = ab.replace("\n", "")
            ab = ab.replace("  ", " ")
            ab = ab.replace("  ", " ")
            ab = ab.replace("\xc2\xa0", "")
            ab = ab.replace("  ", " ")
            ab = ab.replace("\r", "")
            # 飘红
            keyred = """<span style="color:#F08080">%s</span>"""%(tmp_query)
            ab = ab.replace(tmp_query, keyred)
            ab = ab.replace("__hasssss__iiiiiimage__", "")
            return ab 

        terms = query.split(' ')
        abstract_list = []
        for t in terms:
            pos = fc.find(t)
            if pos < 0:
                continue
            left = self.__left_sentence_bound(pos, fc) 
            right = self.__right_sentence_bound(pos, fc)

            ab = fc[left:right]
            ab = ab.replace("\n", "")
            ab = ab.replace("  ", " ")
            ab = ab.replace("\xc2\xa0", "")
            ab = ab.replace("  ", " ")
            ab = ab.replace("  ", " ")
            ab = ab.replace("\r", "")
            keyred = """<span style="color:#F08080">%s</span>"""%(t)
            ab = ab.replace(t, keyred)
            ab = ab.replace("__hasssss__iiiiiimage__", "")
            abstract_list.append(ab)

        if len(abstract_list):
            combine = "...".join(abstract_list)
            return combine[3:]
        return ""

    def __abstract_one(self, query_list, filename):
        if not os.access(filename, os.F_OK):
            return "无摘要信息"
        fd = open(filename, "r")
        fc = fd.read()
        fc = fc.lower()
        fd.close()

        for q in query_list:
            query = q["query"]
            txt = self.__abstract_one_by_query(query, fc)
            if txt != "":
                return txt

    def __abstract(self, query_list, result):
        """
        result is a list
        [0] -> {"doc":, "docid":, "score":}
        """
        
        for i in result:
            for j in result[i]:
                docfile = j["doc"]
                j["abstract"] = self.__abstract_one(query_list, docfile)


    def __query_analyze_has(self, query, operations):
        if query is None or query == "":
            return
        r = operations
        # 精确不切词查询
        r.append({"query": query, "type": "BEST_MATCH"})

        # 去掉空格
        if query.replace(" ", "") != query:
            r.append({"query": query.replace(" ", ""), "type": "BEST_MATCH"})

        # 空格分割, 全排列
        if len(query.split(' ')) <= 4 and len(query.split(' ')) > 1:
            ex = list(itertools.permutations(query.split(' ')))
            for i in ex:
                r.append({"query": ' '.join(i), "type": "BEST_MATCH"})

        # WELL_MATCH 会按空格切割多个 term, 拉链归并
        if ' ' in query:
            r.append({"query": query, "type": "WELL_MATCH"})
            r.append({"query": query, "type": "PART_MATCH"})

        cutword = jieba.cut(query, cut_all=False)
        cutquery = ' '.join(cutword)
        cutquery = cutquery.replace("  ", " ")
        cutquery = cutquery.replace("  ", " ")
        cutquery = cutquery.replace("  ", " ")
        cutquery = cutquery.replace(".", "")

        r.append({"query": cutquery, "type": "WELL_MATCH"})
        r.append({"query": cutquery, "type": "PART_MATCH"})

        # 剔除一个空格
        while cutquery.find(' ') > 0:
            cutquery = cutquery[:cutquery.find(' ')] + cutquery[cutquery.find(' ')+1:]
            r.append({"query": cutquery, "type": "WELL_MATCH"})
            r.append({"query": cutquery, "type": "PART_MATCH"})

    def __query_analyze_not(self, operations, query):
        if query is None or query == "":
            return 
        for i in operations:
            i["mustnot"] = query


    def __query_analyze(self, query):
        """
            把原始 query 扩展出多个检索原语
            [ {"query": "python 第五方", "type": "BEST_MATCH"}, {}, {} ]
        """
        r = []
        if " -" not in query:
            self.__query_analyze_has(query, r) 
        if " -" in query:
            hasquery = query[:query.find(" -")]
            hasquery = hasquery.strip()
            self.__query_analyze_has(hasquery, r)

            mustnot = query[query.find(" -") + 1:]
            mustnot = mustnot.strip()
            self.__query_analyze_not(r, mustnot)
        return r

    def search(self, query):
        query = self.__preprocess(query) 
        if query == "":
            return {}

        seek_query_list = self.__query_analyze(query)

        result = {}
        result["BEST_MATCH"] = [] 
        result["WELL_MATCH"] = [] 
        result["PART_MATCH"] = [] 
        notresult            = []
        donequery = {}
        for op in seek_query_list:
            querysign = "%s%s"%(op["query"], op["type"])
            if querysign in donequery:
                continue
            donequery[querysign] = 1
            logging.debug("query 检索原语: %s" % json.dumps(op, ensure_ascii=False))

            if op["type"] == "BEST_MATCH":
                result["BEST_MATCH"] += self.__search_best_match(op["query"])

            if op["type"] == "WELL_MATCH":
                result["WELL_MATCH"] += self.__search_well_match(op["query"])

            if op["type"] == "PART_MATCH":
                # 全token匹配结果为0时, 使用部分匹配结果
                if len(result["BEST_MATCH"]) + len(result["WELL_MATCH"]) == 0:
                    result["PART_MATCH"] += self.__search_partmatch(op["query"])
                pass

        # 减法
        if "mustnot" in op:
            notresult += self.__search_well_match(op["mustnot"], limit=1000000)
            notresult += self.__search_partmatch(op["mustnot"], limit=1000000)

        for match_type in result:
            result[match_type] = self.__remove_mustnot(result[match_type], notresult)
            result[match_type] = self.__remove_invalid_doc(result[match_type])
            result[match_type] = self.__sort_result(result[match_type])
            result[match_type] = self.__limit(result[match_type], 10)
            result[match_type] = self.__trans_to_docfile(result[match_type])

        # 去重
        result = self.__filter_duplicate(result)

        # 计算摘要
        self.__abstract(seek_query_list, result)

        self.print_result(result)

        result = self.__format_to(result, "LIST")
        return result

def create_wiz_search():
    db = WizIndex()
    db.build_index()
    xxx = jieba.cut_for_search("中华人民共和国")
    yyy = ''.join(xxx)
    return db

if __name__ == "__main__":
    db = create_wiz_search()
    while True:
        print("Please input query:")
        query = sys.stdin.readline()
        query = query.replace("\n", "")
        if query == "":
            continue
        db.search(query)



