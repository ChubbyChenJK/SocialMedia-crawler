# web_api.py
from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import json
import os

app = FastAPI()

SETTINGS_PATH = './weibo/settings.py'

class ScrapeRequest(BaseModel):
    cookie: str = None
    keyword_list: str = None
    start_date: str = None
    end_date: str = None
    download_need: int = None  # 0 or 1
    media_spread: int = None   # 0 or 1
    store: str = None          # csv/mysql/mongo/sqlite

@app.post("/run_spider")
def run_spider(params: ScrapeRequest):
    import API  # 原来的 API.py
    args = params.dict()
    
    class Args:
        def __init__(self, **entries):
            self.__dict__.update(entries)
    args_obj = Args(**args)
    
    API.update_setting_file(args_obj)
    
    # 执行爬虫命令
    result = subprocess.run(['scrapy', 'crawl', 'search'], capture_output=True, text=True)
    
    return {
        "status": "success" if result.returncode == 0 else "failed",
        "stdout": result.stdout,
        "stderr": result.stderr
    }

