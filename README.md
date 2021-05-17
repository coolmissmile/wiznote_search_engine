### 2019-11-07

### Demo
![image](https://github.com/coolmissmile/wiznote_search_engine/blob/master/wiz_demo2.gif)


### 为知笔记-搜索引擎
```
本项目是基于"为知笔记"构建的一个本地搜索引擎, 可以认为是 "为知笔记" + "百度搜索" 的综合效果
可以实时解析笔记本本机的为知笔记数据, 搜索速度比原始wiz笔记快很多
```

```
这套搜索引擎的基本特性是:
[1] 目前仅支持 Mac 平台, 主要用 shell + python实现
[2] 自动解析搜索笔记本本地数据
[3] 使用浏览器 web 页面做为搜索入口
[3] 支持 query 和文本切词
[4] 基本原理是使用倒排索引 和 检索拉链归并
[5] 排序算法一期支持query分词、TFIDF文本相关性、Term紧密度策略、标题提取、高端排序策略。
    二期计划支持Query改写，Term重要性策略以及上下位概念提取等
[6] 支持 markdown 格式自动渲染
[7] 支持 减法语法查询
[8] 支持摘要自动提取和关键词飘红
[9] 自动适应新增的笔记和删除的笔记(1分钟延迟)
[10] 搜索结果可以使用网页形式查看, 也可以链接跳转到为知笔记客户端内
```

### 为知笔记官网
```
http://www.wiz.cn/zh-cn
```

### Install 安装
```
[1] 先从为知笔记官网下载mac 版客户端, 登录自己的账户, 创建笔记
[2] 下载本工具到mac笔记本任意目录, 然后执行:
    bash start.sh
    Wait for 2min for success
```

### Search 搜索
```
使用搜索功能, 打开浏览器, 输入 http://127.0.0.1:9009
然后会出现和百度类似的搜索框, 输入要搜索的内容点击搜索即可

open http://127.0.0.1:9009 on your chrome or safair
```

### Change Listen Port 修改端口
```
本工具默认启动端口是 9009
如果和本机其他软件端口冲突了, 可以修改为其他任意端口, 比如修改为 18080
bash change_to_port.sh 18080
bash start.sh
```

### Error log 查看日志
```
cat error.log
```


### 联系我
```
mailto  1256268688@qq.com
```
