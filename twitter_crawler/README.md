# Twitter Crawler API 使用说明

## 功能

本工具通过命令行运行 `API.py`，根据用户在命令行传入的参数配置，自动抓取 Twitter 用户或关键词内容，并下载相关媒体（图片、视频）或文本。  
具备以下功能：

- 支持按用户名（user 模式）或关键词（content 模式）抓取推文；
- 可设置抓取时间范围；
- 支持媒体（图片、视频）或文本模式；
- 结果自动保存为 CSV 文件；
- 多用户/多关键词批量处理。

---

## 输出

根据运行模式不同，输出内容如下：

### user 模式（调用执行 `main.py`）：

- `/用户名/` 文件夹：
  - 推文图片/视频；
  - `.csv`：包含推文内容及统计信息。

### content 模式（调用执行 `tag_down.py`）：

- `/关键词或标签/` 文件夹：
  - 媒体文件或文本内容；
  - `.csv`：包含推文内容及统计信息。

其中，csv 文件包含以下字段：
- 媒体 mode：Tweet Date, Display Name, User Name, Tweet URL, Tweet Content, Favorite Count, Retweet Count, Reply Count
- 文本 mode：Tweet Date, Display Name, User Name, Tweet URL, Media Type, Media URL, Saved Filename, Tweet Content, Favorite Count, Retweet Count, Reply Count

---


## 使用说明

### 1. 安装依赖

确保你已安装 Python 3.8+，并执行以下命令安装依赖：

```bash
pip install -r requirements.txt
```

### 2. 运行 API.py
👤 用户模式：抓取指定用户在指定时间范围内发布的所有内容，包括文本、图片和视频。需要指定的参数如下：
```bash
python API.py \
  --cookie "auth_token=xxx; ct0=xxx;" \
  --filter user \
  --username "用户名（如lilmonix3）" \
  --start_date 2017-01-01 \
  --end_date 2017-12-31
```
🔍 内容模式：按关键词抓取推文，可选择抓取包含媒体（图片+视频）的帖子；或仅包含文本内容的帖子。需要指定的参数如下：
```bash
python API.py \
  --cookie "auth_token=xxx; ct0=xxx;" \
  --filter content \
  --keyword "Trump,USA" \
  --start_date 2024-01-01 \
  --end_date 2024-01-02 \
  --mode media/text \
  --down_count 最大下载数量（必须为50的倍数，最小50。实际下载数量会略大于该值）

```

## 如何获取 Cookie
打开你的浏览器并登录 Twitter；

按下 F12 打开开发者工具，切换到 Application 或 Network 标签页，找到 Cookies 的 auth_token 和 ct0 字段并复制它们的值：

```text
auth_token=xxxxx; ct0=xxxxx;
```
并作为 --cookie 参数传入。