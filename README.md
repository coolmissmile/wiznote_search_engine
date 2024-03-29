### 2019-11-07

### Demo
![image](https://github.com/coolmissmile/wiznote_search_engine/blob/master/wiz_demo2.gif)


### 为知笔记-搜索引擎
```
本项目是基于"为知笔记"构建的一个本地搜索引擎, 可以认为是 "为知笔记" + "百度搜索" 的综合效果
可以实时解析笔记本本机的为知笔记数据, 搜索速度比原始wiz笔记快很多
```

### 使用方法
```
这套搜索引擎的基本特性是:
[*] 搜索速度比为知笔记本身快几十倍，毫秒级出结果 
[*] 搜索结果可以点击跳转到为知客户端(见demo视频)
[*] 使用浏览器 web 页面做为搜索入口
[*] 目前仅支持 Mac 平台, 主要用 python + shell 实现
[*] 自动寻找笔记本本地数据, 无需手动拷贝文件
[*] 实时增量笔记更新和删除(1分钟延迟)
[*] 支持 markdown 格式自动渲染
[*] 支持 减法语法查询
[*] 绝对安全，不会把内容上传到某某网站
```

### 基本原理
```
这是一个完整的搜索引擎雏形，麻雀虽小五脏俱全，搜索核心过程和百度、Google等类似。
引擎的核心过程有抓取、分词、构建倒排数据、query变换、拉链归并、TF-IDF基础相关性排序、term过滤策略和结合高端排序策略。

```

### 搜索策略
```
[*] query分词
[*] query改写
[*] query扩展
[*] query忽略
[*] query上下位概念提取
[*] TF-IDF文本相关性
[*] TERM紧密度策略
[*] TERM重要性策略
[*] 提权策略（标题提权、权威性提权）
[*] 高端排序策略(特殊标记提权、markdown提权、时效性提权)

```



### 为知笔记官网
```
http://www.wiz.cn/zh-cn

只支持旧版本 为知笔记客户端: https://url.wiz.cn/u/macold  最高版本v2.8.7
2021年新版本的暂时还不支持 
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

### 集成到 Alfred
```
# 步骤
1. 打开Alfred设置
2. Features -> Web Search
3. 右下角点击 “Add Custom Search”
4. search URL 填写：  http://127.0.0.1:9009/?query={query}
   Title 填写： 搜索 为知笔记
   Keyword 填写： s
5. 点击Save，即可
6. 使用方式：快捷键唤出Alfred ， 输入： s {加个空格}  关键词 

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
