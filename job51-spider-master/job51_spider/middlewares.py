# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html
import os
import time, datetime
import redis
import random
from scrapy import signals
from scrapy.exceptions import NotConfigured
from share import REDIS_DB, REDIS_PWD, REDIS_HOST, REDIS_PORT
from scrapy.http import HtmlResponse
from scrapy.http import Request
import requests
from scrapy.http.cookies import CookieJar
from share import random_user_agent
from share import RandomMonitoringMiddleware, RedisSpiderSmartIdleClosedExensions
from share import MYSQL_PORT, MYSQL_CHARSET, MYSQL_DATA_DB, MYSQL_PASSWD, MYSQL_USER, MYSQL_HOST
from scrapy.http.headers import Headers
from scrapy.exceptions import IgnoreRequest
import pymysql

#代理模式
class ProxyMiddleware(object):
    # 连接redis,从redis数据库获取可用的ip池
    def __init__(self, crawler):
        self.counter = 0
        self.proxies = []
        self.start_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        self.max_failed = 0
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(crawler)
        if not crawler.settings.getbool('HTTPPROXY_ENABLED'):
            raise NotConfigured
        return s

    def get_proxy(self):
        self.counter += 1
        print('代理启用次数', self.counter)
        REDIS_DB='0'
        self.myredis = redis.Redis(host=REDIS_HOST, password=REDIS_PWD, port=REDIS_PORT, db=REDIS_DB)
        total_ip = int(self.myredis.llen('useful_proxy'))
        print('total_ip', total_ip)
        if total_ip:
            total = total_ip
        else:
            total = 5
        proxy_ = self.myredis.lindex('useful_ip', random.randint(1, total - 1)).decode('utf-8')
        return proxy_

    def get_redis_proxy(self):
        myredis = redis.Redis(host=REDIS_HOST, password=REDIS_PWD, port=REDIS_PORT, db="0")
        proxies = myredis.hgetall('useful_proxy')
        return random.choice([x.decode() for x in proxies])

    def process_request(self, request, spider):
        User_Agent = random_user_agent().computer_user_agent()
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "DNT": "1",
            "Host": "search.51job.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": User_Agent
        }
        if 'jobterm' in request.url or 'search.51job.com' in request.url or 'jobs.51job' in request.url:
            request.meta['proxy'] = 'http://' + self.get_redis_proxy()
            request.headers = Headers(headers)
            print('=' * 10, request.meta['proxy'])
            time.sleep(random.uniform(1, 2))
        else:
            raise IgnoreRequest


    def process_response(self, request, response, spider):
        print('response.status', response.status)
        if response.status == 407:
            self.max_failed += 1
            print('self.max_failed', self.max_failed)
            User_Agent = random_user_agent().computer_user_agent()
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "DNT": "1",
                "Host": "search.51job.com",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": User_Agent
            }
            res = requests.get(request.url, proxies={'http': "http://" + self.get_proxy()},
                               headers = headers)
            res.encoding = 'utf-8'
            content = res.text
            print(request.headers, headers)
            return HtmlResponse(request.url, encoding='utf-8', body=content, request=request)
        else:
            return response

#非代理模式
class NoProxyMiddleware(object):
    def __init__(self, settings):
        self.myredis = redis.Redis(host=REDIS_HOST, password=REDIS_PWD, port=REDIS_PORT, db=REDIS_DB)


    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls(crawler.settings)
        return s

    def process_request(self, request, spider):
        User_Agent = random_user_agent().computer_user_agent()
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": User_Agent,
            "DNT": "1",
        }
        #request.headers = Headers(headers)
        pass


    def process_response(self, request, response, spider):
        print(response.status, '-*' * 20)
        print(request.url)
        if response.status >=400:
            User_Agent = random_user_agent().computer_user_agent()
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "Accept-Encoding": "gzip, deflate",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "User-Agent": User_Agent,
                "DNT": "1",

            }
            request.headers = Headers(headers)
            return request
        else:
            return response

#初始化去重url
class HashtoRedisMiddleware(object):
    def __init__(self, settings):
        self.myredis = redis.Redis(host=REDIS_HOST, password=REDIS_PWD, port=REDIS_PORT, db=REDIS_DB)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls(crawler.settings)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
        # 爬虫打开的是否将对应的爬虫的hash字段写入redis中，从mysql基础表获取redis-key信息
        # 连接mysql
        connect = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWD, MYSQL_DATA_DB, charset=MYSQL_CHARSET,
                                  port=MYSQL_PORT)
        cursor = connect.cursor()

        # 把去重hash填入
        for table in spider.table:
            exists_or_not = self.myredis.exists(table)
            if not exists_or_not:
                # redis不存在该字段，则插入
                start = 1
                step = 5000
                while True:
                    get_hash_id_sql = 'select url from %s limit %s,%s;' % (table, start,  step)
                    cursor.execute(get_hash_id_sql)
                    connect.commit()
                    tuples1 = cursor.fetchall()
                    if len(tuples1) > 1:
                        for index, onedata in enumerate(tuples1):
                            hashid = onedata[0]
                            self.myredis.sadd(table, hashid.encode('utf-8'))
                        start = start + step
                    else:
                        break
        cursor.close()
        connect.close()

