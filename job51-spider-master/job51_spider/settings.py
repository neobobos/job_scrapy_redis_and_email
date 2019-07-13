# -*- coding: utf-8 -*-

from config import *

BOT_NAME = 'job51_spider'

SPIDER_MODULES = ['job51_spider.spiders']
NEWSPIDER_MODULE = 'job51_spider.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
LOG_LEVEL = 'DEBUG'
COOKIES_ENABLED = True
COOKIES_DEBUG = False
RETRY_ENABLED = True
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 404,407, 408, 301, 302]
RETRY_TIMES = 3

# 分布式配置
import scrapy_redis
SCHEDULER_PERSIST = True
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'


DOWNLOADER_MIDDLEWARES = {
    'job51_spider.middlewares.RedisSpiderSmartIdleClosedExensions': 728,
    'job51_spider.middlewares.ProxyMiddleware': None,
    'job51_spider.middlewares.NoProxyMiddleware': 200,
    'job51_spider.middlewares.HashtoRedisMiddleware': 300,
    "job51_spider.middlewares.RandomMonitoringMiddleware": 543
}

ITEM_PIPELINES = {
    'job51_spider.pipelines.MysqlPipeline': 250
}

