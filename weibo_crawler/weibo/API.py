# weiboAPI.py
import argparse
import os
import json

SETTINGS_PATH = './settings.py'

def update_setting_file(args):
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    def replace_setting(lines, key, value, is_list=False):
        updated_lines = []
        replaced = False
        for line in lines:
            if line.strip().startswith(f'{key} ='):
                if is_list:
                    value_str = json.dumps(value, ensure_ascii=False)
                else:
                    value_str = f"'{value}'" if isinstance(value, str) else str(value)
                updated_lines.append(f"{key} = {value_str}\n")
                replaced = True
            else:
                updated_lines.append(line)
        if not replaced:
            updated_lines.append(f"{key} = {value_str}\n")
        return updated_lines

    # Update each specified setting
    if args.cookie:
        cookie_line = f"'cookie': '{args.cookie}',\n"
        lines = [
            line if "'cookie':" not in line else f"    {cookie_line}"
            for line in lines
        ]
    if args.keyword_list:
        keywords = args.keyword_list.split(',') if ',' in args.keyword_list else [args.keyword_list]
        lines = replace_setting(lines, 'KEYWORD_LIST', keywords, is_list=True)
    if args.start_date:
        lines = replace_setting(lines, 'START_DATE', args.start_date)
    if args.end_date:
        lines = replace_setting(lines, 'END_DATE', args.end_date)
    if args.download_need is not None:
        lines = replace_setting(lines, 'DOWNLOAD_NEED', int(args.download_need))
    if args.media_spread is not None:
        lines = replace_setting(lines, 'MEDIA_SPREAD', int(args.media_spread))

    if args.store:
        store = args.store.lower()
        pipelines = {
            'csv': "'weibo.pipelines.CsvPipeline': 301",
            'mysql': "'weibo.pipelines.MysqlPipeline': 302",
            'mongo': "'weibo.pipelines.MongoPipeline': 303",
            'sqlite': "'weibo.pipelines.SQLitePipeline': 306",
        }
        
        # 数据库配置模板
        db_configs = {
            'mysql': [
                "MYSQL_HOST = 'localhost'\n",
                "MYSQL_PORT = 3306\n",
                "MYSQL_USER = 'root'\n",
                "MYSQL_PASSWORD = '123456'\n",
                "MYSQL_DATABASE = 'weibo'\n"
            ],
            'mongo': [
                "MONGO_URI = 'localhost'\n"
            ],
            'sqlite': [
                "SQLITE_DATABASE = 'weibo.db'\n"
            ]
        }
        
        lines = [line for line in lines if 'pipelines.' not in line or store in line]
        
        # 处理数据库配置
        # 首先移除所有现有的数据库配置（注释或非注释）
        db_keys = ['MONGO_URI', 'MYSQL_HOST', 'MYSQL_PORT', 'MYSQL_USER', 
                'MYSQL_PASSWORD', 'MYSQL_DATABASE', 'SQLITE_DATABASE']
        lines = [line for line in lines if not any(key in line for key in db_keys)]
        
        # 添加新的数据库配置（如果是数据库类型）
        new_db_config = []
        if store in db_configs:
            new_db_config = db_configs[store]
        
        new_pipeline_lines = [
            "ITEM_PIPELINES = {\n",
            "    'weibo.pipelines.DuplicatesPipeline': 300,\n"
        ]
        if store in pipelines:
            new_pipeline_lines.append(f"    {pipelines[store]},\n")
        new_pipeline_lines.append("}\n")
        
        # 移除旧的ITEM_PIPELINES块
        in_pipeline = False
        cleaned_lines = []
        for line in lines:
            if line.strip().startswith('ITEM_PIPELINES'):
                in_pipeline = True
                continue
            if in_pipeline and line.strip().startswith('}'):
                in_pipeline = False
                continue
            if not in_pipeline:
                cleaned_lines.append(line)
        
        # 合并所有内容：原始清理后的内容 + 数据库配置 + 管道配置
        lines = cleaned_lines + new_db_config + new_pipeline_lines

    # 写回更新后的settings
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.writelines(lines)


def main():
    parser = argparse.ArgumentParser(description='Weibo Scraper API')
    parser.add_argument('--cookie', help='Weibo cookie string')
    parser.add_argument('--keyword_list', help='Comma-separated keywords or txt file path')
    parser.add_argument('--start_date', help='Start date (yyyy-mm-dd)')
    parser.add_argument('--end_date', help='End date (yyyy-mm-dd)')
    parser.add_argument('--download_need', type=int, choices=[0, 1], help='Whether to download media (0/1)')
    parser.add_argument('--media_spread', type=int, choices=[0, 1], help='Whether to spread media (0/1)')
    parser.add_argument('--store', choices=['csv', 'mysql', 'mongo', 'sqlite'], help='Storage method')

    args = parser.parse_args()
    update_setting_file(args)

    print('Running: scrapy crawl search\n')
    os.system('scrapy crawl search')

if __name__ == '__main__':
    main()
