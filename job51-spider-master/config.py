"""
    PUBLIC MODULE
"""

MYSQL_HOST ='127.0.0.1'
MYSQL_USER = '****'  #
MYSQL_PASSWD = '****'  #
MYSQL_PORT = 3306
MYSQL_DATA_DB = '****'
MYSQL_CHARSET = 'utf8mb4'

REDIS_URL = 'redis://:@127.0.0.1:6379/10'
REDIS_HOST="127.0.0.1"
REDIS_PWD=''
REDIS_PORT=6379
REDIS_DB=10

# user_agent
import faker
class random_user_agent():
    def __init__(self):
        self.f = faker.Faker("zh_CN")

    # computer_user_agent
    def computer_user_agent(self):
        while True:
            user_agent = self.f.user_agent()
            if 'iPhone' not in user_agent and 'iPad' not in user_agent \
                and 'iPod' not in user_agent and 'iOS' not in user_agent \
                and 'android' not in user_agent and 'nexus' not in user_agent \
                and 'Phone' not in user_agent and 'BlackBerry' not in user_agent \
                and 'MicroMessenger' not in user_agent:
                break
        return user_agent


# scrapy-redis
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# Empty running setting
MYEXT_ENABLED=True
IDLE_NUMBER=120

# empty running Middleware
import redis
import time
class RedisSpiderSmartIdleClosedExensions(object):

    def __init__(self, idle_number, crawler):
        self.crawler = crawler
        self.idle_number = idle_number
        self.idle_list = []
        self.idle_count = 0
        self.myredis = redis.Redis(host=REDIS_HOST, password=REDIS_PWD, port=REDIS_PORT, db=REDIS_DB)

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool('MYEXT_ENABLED'):
            raise NotConfigured

        if not 'redis_key' in crawler.spidercls.__dict__.keys():
            raise NotConfigured('Only supports RedisSpider')
        idle_number = crawler.settings.getint('IDLE_NUMBER', 360)
        ext = cls(idle_number, crawler)
        crawler.signals.connect(ext.spider_idle, signal=signals.spider_idle)
        return ext


    def spider_idle(self, spider):
        self.idle_count += 1
        self.idle_list.append(time.time())
        idle_list_len = len(self.idle_list)

        if idle_list_len > 2 and spider.server.exists(spider.redis_key):
            self.idle_list = [self.idle_list[-1]]
        elif idle_list_len > self.idle_number:
            self.crawler.engine.close_spider(spider, 'closespider_pagecount')


# Monitoring Middleware
from scrapy import signals
from scrapy.exceptions import NotConfigured
class RandomMonitoringMiddleware(object):
    def __init__(self, settings):
        self.myredis = redis.Redis(host=REDIS_HOST,password=REDIS_PWD,port=REDIS_PORT,db=REDIS_DB)

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls(crawler.settings)
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def spider_opened(self,spider):
        if self.myredis.hget("@" + spider.name, 'stop_time') != b'--':
            self.myredis.hset("@" + spider.name, 'start_time', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
            self.myredis.hset("@" + spider.name, 'stop_time', '--')
            self.myredis.hdel('@' + spider.name, 'source_table_num')
            self.myredis.hdel('@' + spider.name, 'old_current_progress')
            self.myredis.hdel("@" + spider.name, 'current_progress')
            self.myredis.hdel("@" + spider.name, 'insert_sql_count')
            self.myredis.hdel("@" + spider.name, 'old_insert_sql_count')

    def process_request(self,  request, spider):
        pass

    def process_response(self,request,response,spider):
        if 200 <= response.status < 300:
            self.myredis.hincrby("@"+spider.name, 'status_200', 1)
        elif 300 <= response.status < 400:
            self.myredis.hincrby("@"+spider.name, 'status_300', 1)
        elif 400 <= response.status < 500:
            self.myredis.hincrby("@"+spider.name, 'status_400', 1)
        elif 500 <= response.status < 600:
            self.myredis.hincrby("@"+spider.name, 'status_500', 1)

        return response

    def process_exception(self,request,exception,spider):
        pass

    def spider_closed(self,spider):
        self.myredis.hset("@" + spider.name, 'stop_time',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() - 1800)))

