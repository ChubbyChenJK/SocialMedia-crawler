## 功能
连续获取一个或多个**微博关键词搜索**结果，并将结果写入文件（可选）、数据库（可选）等。所谓微博关键词搜索即：**搜索正文中包含指定关键词的微博**，可以指定搜索的时间范围。<br>
本程序可以获得几乎全部的微博信息，如微博正文、发布者等，详情见[输出](#输出)部分。支持输出多种文件类型，具体如下：
- 写入**csv文件**
- 写入**MySQL数据库**
- 写入**MongoDB数据库**
- 写入**Sqlite数据库**（无需外部安装，相比MySQL和MongoDB更方便）
- 下载微博中的**图片**
- 下载微博中的**视频**

## 输出
- 微博id：微博的id，为一串数字形式
- 微博bid：微博的bid
- 微博内容：微博正文
- 头条文章url：微博中头条文章的url，若某微博中不存在头条文章，则该值为''
- 原始图片url：原创微博图片和转发微博转发理由中图片的url，若某条微博存在多张图片，则每个url以英文逗号分隔，若没有图片则值为''
- 视频url: 微博中的视频url和Live Photo中的视频url，若某条微博存在多个视频，则每个url以英文分号分隔，若没有视频则值为''
- 微博发布位置：位置微博中的发布位置
- 微博发布时间：微博发布时的时间，精确到天
- 点赞数：微博被赞的数量
- 转发数：微博被转发的数量
- 评论数：微博被评论的数量
- 微博发布工具：微博的发布工具，如iPhone客户端、HUAWEI Mate 20 Pro等，若没有则值为''
- 话题：微博话题，即两个#中的内容，若存在多个话题，每个url以英文逗号分隔，若没有则值为''
- @用户：微博@的用户，若存在多个@用户，每个url以英文逗号分隔，若没有则值为''
- 原始微博id：为转发微博所特有，是转发微博中那条被转发微博的id，那条被转发的微博也会存储，字段和原创微博一样，只是它的本字段为空
- 结果文件：保存在当前目录“结果文件”文件夹下以关键词为名的文件夹里
- 微博图片：微博中的图片，保存在以关键词为名的文件夹下的images文件夹里
- 微博视频：微博中的视频，保存在以关键词为名的文件夹下的videos文件夹里
- user_authentication：微博用户类型，值分别是`蓝v`，`黄v`，`红v`，`金v`和`普通用户`

## 使用说明
### 1.安装Scrapy
本程序依赖Scrapy，要想运行程序，需要安装Scrapy。如果系统中没有安装Scrapy，请根据自己的系统安装Scrapy，以Ubuntu为例，可以使用如下命令：
```bash
$ pip install scrapy
```
### 2.安装依赖
```bash
$ pip install -r requirements.txt
```

### 3.运行API.py
运行 API.py 程序，通过命令行参数指定指定cookie、关键词列表、起止日期、是否下载图片视频、是否按照传播度排序、存储方式。以下为各参数的含义与取值范围：
- `--cookie`：微博登录后的cookie，字符串类型。如何获取cookie详见[如何获取cookie](#如何获取cookie)，获取后将"your cookie"替换成真实的cookie即可。
- `--keyword_list`：关键词列表，字符串类型。多个关键词用英文逗号分隔。
- `--start_date`：发布时间起始日期，字符串类型，格式为“yyyy-mm-dd”。
- `--end_date`：发布时间结束日期，字符串类型，格式为“yyyy-mm-dd”。
- `--download_need`：是否下载帖子中包含的图片和视频，整数类型，取值为0或1，0表示不下载，1表示下载。下载的视频和图片以对应帖子id命名。
- `--media_spread`：是否按照传播度排序，整数类型，取值为0或1，0表示不排序，1表示按照传播度从高到低排列（计算方式参照[清博智能](http://gsdata.cn/site/usage-16)）。
- `--store`：存储方式，字符串类型，取值为“csv”、“mysql”、“mongodb”、“sqlite”。如果选择“mysql”或“mongodb”，程序会使用默认的数据库信息，相关信息可在API.py 的 db_configs 中修改。

以下是一个运行示例：
```bash
python API.py --cookie "your cookie" --keyword_list "上海交通大学,电子科技大学" --start_date 2024-05-10 --end_date 2024-05-10 --download_need 1 --media_spread 1 --store csv
```

## 如何获取cookie
1. 用Chrome打开 https://weibo.com/
2. 点击"立即登录", 完成私信验证或手机验证码验证, 进入新版微博. 如下图所示:
<img src="https://user-images.githubusercontent.com/41314224/144813569-cfb5ad32-22f0-4841-afa9-83184b2ccf6f.png" width="400px" alt="...">
3. 按F12打开开发者工具, 在开发者工具的 Network->Name->weibo.cn->Headers->Request Headers, 找到"Cookie:"后的值, 这就是我们要找的cookie值, 复制即可, 如图所示:
<img src="https://github.com/dataabc/media/blob/master/weiboSpider/images/cookie3.png" width="400px" alt="...">

> ## 兼容性说明: 获取旧版微博的Cookie
> 1.用Chrome打开<https://passport.weibo.cn/signin/login>；<br>
> 2.输入微博的用户名、密码，登录，如图所示：
> ![](https://github.com/dataabc/media/blob/master/weiboSpider/images/cookie1.png)
> 登录成功后会跳转到<https://m.weibo.cn>;<br>
> 3.按F12键打开Chrome开发者工具，在地址栏输入并跳转到<https://weibo.cn>，跳转后会显示如下类似界面:
> ![](https://github.com/dataabc/media/blob/master/weiboSpider/images/cookie2.png)
> 4.依此点击Chrome开发者工具中的Network->Name中的weibo.cn->Headers->Request Headers，"Cookie:"后的值即为我们要找的cookie值，复制即可，如图所示：
> ![](https://github.com/dataabc/media/blob/master/weiboSpider/images/cookie3.png)
