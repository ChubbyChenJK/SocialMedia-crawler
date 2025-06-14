# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import copy
import csv
import os

import scrapy
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings

settings = get_project_settings()


class CsvPipeline(object):
    def __init__(self):
        self.items_by_keyword = {}

    def process_item(self, item, spider):
        keyword = item['keyword']
        if keyword not in self.items_by_keyword:
            self.items_by_keyword[keyword] = []
        self.items_by_keyword[keyword].append(item)
        return item

    def close_spider(self, spider):
        media_spread = settings.get('MEDIA_SPREAD', 0)
        for keyword, items in self.items_by_keyword.items():
            base_dir = '结果文件' + os.sep + keyword
            if not os.path.isdir(base_dir):
                os.makedirs(base_dir)
            file_path = os.path.join(base_dir, f"{keyword}.csv")
            is_first_write = not os.path.isfile(file_path)

            # 根据传播度排序
            if media_spread != 0:
                def calc_spread(it):
                    weibo = it['weibo']
                    return (
                        0.17 * int(weibo.get('attitudes_count', 0)) +
                        0.37 * int(weibo.get('comments_count', 0)) +
                        0.46 * int(weibo.get('reposts_count', 0))
                    )
                items.sort(key=calc_spread, reverse=True)

            with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                if is_first_write:
                    header = [
                        'id', 'bid', 'user_id', '用户昵称', '微博正文', '头条文章url',
                        '发布位置', '艾特用户', '话题', '转发数', '评论数', '点赞数', '发布时间',
                        '发布工具', '微博图片url', '微博视频url', 'retweet_id', 'ip', 'user_authentication',
                        '会员类型', '会员等级'
                    ]
                    writer.writerow(header)

                for item in items:
                    weibo = item['weibo']
                    writer.writerow([
                        weibo.get('id', ''),
                        weibo.get('bid', ''),
                        weibo.get('user_id', ''),
                        weibo.get('screen_name', ''),
                        weibo.get('text', ''),
                        weibo.get('article_url', ''),
                        weibo.get('location', ''),
                        weibo.get('at_users', ''),
                        weibo.get('topics', ''),
                        weibo.get('reposts_count', ''),
                        weibo.get('comments_count', ''),
                        weibo.get('attitudes_count', ''),
                        weibo.get('created_at', ''),
                        weibo.get('source', ''),
                        ','.join(weibo.get('pics', [])),
                        weibo.get('video_url', ''),
                        weibo.get('retweet_id', ''),
                        weibo.get('ip', ''),
                        weibo.get('user_authentication', ''),
                        weibo.get('vip_type', ''),
                        weibo.get('vip_level', 0)
                    ])

class SQLitePipeline(object):
    def __init__(self):
        self.items = []

    def open_spider(self, spider):
        try:
            import sqlite3
            base_dir = '结果文件'
            if not os.path.isdir(base_dir):
                os.makedirs(base_dir)
            db_name = settings.get('SQLITE_DATABASE', 'weibo.db')
            self.conn = sqlite3.connect(os.path.join(base_dir, db_name))
            self.cursor = self.conn.cursor()
            sql = """
            CREATE TABLE IF NOT EXISTS weibo (
                id varchar(20) NOT NULL PRIMARY KEY,
                bid varchar(12) NOT NULL,
                user_id varchar(20),
                screen_name varchar(30),
                text varchar(2000),
                article_url varchar(100),
                topics varchar(200),
                at_users varchar(1000),
                pics varchar(3000),
                video_url varchar(1000),
                location varchar(100),
                created_at DATETIME,
                source varchar(30),
                attitudes_count INTEGER,
                comments_count INTEGER,
                reposts_count INTEGER,
                retweet_id varchar(20),
                ip varchar(100),
                user_authentication varchar(100),
                vip_type varchar(50),
                vip_level INTEGER
            )"""
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(f"SQLite数据库创建失败: {e}")
            spider.sqlite_error = True

    def process_item(self, item, spider):
        self.items.append(copy.deepcopy(item))
        return item

    def close_spider(self, spider):
        media_spread = settings.get('MEDIA_SPREAD', 0)
        if media_spread != 0:
            def calc_spread(it):
                w = it['weibo']
                return (
                    0.17 * int(w.get('attitudes_count', 0)) +
                    0.37 * int(w.get('comments_count', 0)) +
                    0.46 * int(w.get('reposts_count', 0))
                )
            self.items.sort(key=calc_spread, reverse=True)

        for item in self.items:
            try:
                data = dict(item['weibo'])
                data['pics'] = ','.join(data['pics'])
                keys = ', '.join(data.keys())
                placeholders = ', '.join(['?'] * len(data))
                sql = f"""INSERT OR REPLACE INTO weibo ({keys}) 
                         VALUES ({placeholders})"""
                self.cursor.execute(sql, tuple(data.values()))
                self.conn.commit()
            except Exception as e:
                print(f"SQLite保存出错: {e}")
                spider.sqlite_error = True
                self.conn.rollback()
        self.conn.close()

class MongoPipeline(object):
    def __init__(self):
        self.items = []

    def open_spider(self, spider):
        try:
            from pymongo import MongoClient
            self.client = MongoClient(settings.get('MONGO_URI'))
            self.db = self.client['weibo']
            self.collection = self.db['weibo']
        except ModuleNotFoundError:
            spider.pymongo_error = True

    def process_item(self, item, spider):
        self.items.append(copy.deepcopy(item))
        return item

    def close_spider(self, spider):
        import pymongo
        media_spread = settings.get('MEDIA_SPREAD', 0)
        if media_spread != 0:
            def calc_spread(it):
                w = it['weibo']
                return (
                    0.17 * int(w.get('attitudes_count', 0)) +
                    0.37 * int(w.get('comments_count', 0)) +
                    0.46 * int(w.get('reposts_count', 0))
                )
            self.items.sort(key=calc_spread, reverse=True)

        for item in self.items:
            try:
                if not self.collection.find_one({'id': item['weibo']['id']}):
                    self.collection.insert_one(dict(item['weibo']))
                else:
                    self.collection.update_one(
                        {'id': item['weibo']['id']},
                        {'$set': dict(item['weibo'])}
                    )
            except pymongo.errors.ServerSelectionTimeoutError:
                spider.mongo_error = True

        try:
            self.client.close()
        except AttributeError:
            pass


class MysqlPipeline(object):
    def __init__(self):
        self.items = []

    def create_database(self, mysql_config):
        import pymysql
        sql = """CREATE DATABASE IF NOT EXISTS %s DEFAULT
            CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci""" % settings.get(
            'MYSQL_DATABASE', 'weibo')
        db = pymysql.connect(**mysql_config)
        cursor = db.cursor()
        cursor.execute(sql)
        db.close()

    def create_table(self):
        sql = """
                CREATE TABLE IF NOT EXISTS weibo (
                id varchar(20) NOT NULL,
                bid varchar(12) NOT NULL,
                user_id varchar(20),
                screen_name varchar(30),
                text varchar(2000),
                article_url varchar(100),
                topics varchar(200),
                at_users varchar(1000),
                pics varchar(3000),
                video_url varchar(1000),
                location varchar(100),
                created_at DATETIME,
                source varchar(30),
                attitudes_count INT,
                comments_count INT,
                reposts_count INT,
                retweet_id varchar(20),
                PRIMARY KEY (id),
                ip varchar(100),
                user_authentication varchar(100),
                vip_type varchar(50),
                vip_level INT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
        self.cursor.execute(sql)

    def open_spider(self, spider):
        import pymysql
        try:
            mysql_config = {
                'host': settings.get('MYSQL_HOST', 'localhost'),
                'port': settings.get('MYSQL_PORT', 3306),
                'user': settings.get('MYSQL_USER', 'root'),
                'password': settings.get('MYSQL_PASSWORD', '123456'),
                'charset': 'utf8mb4'
            }
            self.create_database(mysql_config)
            mysql_config['db'] = settings.get('MYSQL_DATABASE', 'weibo')
            self.db = pymysql.connect(**mysql_config)
            self.cursor = self.db.cursor()
            self.create_table()
        except ImportError:
            spider.pymysql_error = True
        except pymysql.OperationalError:
            spider.mysql_error = True

    def process_item(self, item, spider):
        self.items.append(copy.deepcopy(item))
        return item

    def close_spider(self, spider):
        media_spread = settings.get('MEDIA_SPREAD', 0)
        if media_spread != 0:
            def calc_spread(it):
                w = it['weibo']
                return (
                    0.17 * int(w.get('attitudes_count', 0)) +
                    0.37 * int(w.get('comments_count', 0)) +
                    0.46 * int(w.get('reposts_count', 0))
                )
            self.items.sort(key=calc_spread, reverse=True)

        for item in self.items:
            data = dict(item['weibo'])
            data['pics'] = ','.join(data['pics'])
            keys = ', '.join(data.keys())
            values = ', '.join(['%s'] * len(data))
            sql = f"""INSERT INTO weibo ({keys}) VALUES ({values}) 
                      ON DUPLICATE KEY UPDATE """
            update = ','.join([f"{key} = VALUES({key})" for key in data])
            sql += update
            try:
                self.cursor.execute(sql, tuple(data.values()))
                self.db.commit()
            except Exception:
                self.db.rollback()

        try:
            self.db.close()
        except Exception:
            pass



class DuplicatesPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['weibo']['id'] in self.ids_seen:
            raise DropItem("过滤重复微博: %s" % item)
        else:
            self.ids_seen.add(item['weibo']['id'])
            return item
