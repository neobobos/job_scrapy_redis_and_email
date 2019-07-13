# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
import re
import time,datetime
import random
from lxml import etree
from job51_spider.items import Job_51job_Item
import hashlib
from urllib.parse  import unquote
import faker
import redis
from config import REDIS_DB,REDIS_PWD,REDIS_HOST,REDIS_PORT

class Job_51job_Spider(RedisSpider):
    table= [Job_51job_Item.table_name]
    name = 'job_51job_spider'
    redis_key = 'job_51job_spider:start_urls'
    myredis = redis.Redis(host=REDIS_HOST, password=REDIS_PWD, port=REDIS_PORT, db=REDIS_DB)

    def __init__(self):
        super(Job_51job_Spider, self).__init__()

    custom_settings = {
        'CONCURRENT_REQUESTS':1,
        'REDIS_START_URLS_AS_SET': True,
        "LOG_LEVEL":'INFO',
        "DOWNLOAD_DELAY":random.randint(3,4),
        "REDIRECT_ENABLED" :False
    }

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "Host": "search.51job.com",
        "User-Agent": faker.Faker().user_agent()
    }


    #爬取列表页面
    def parse(self, response):
        print(response.url)
        jobterm = "全职"
        html_ = response.text
        html_list = etree.HTML(html_)
        jobs_list = html_list.xpath('//div[@class="el"]')

        isnull=re.findall('(对不起，没有找到符合你条件的职位)',response.text)
        if len(isnull)==0:
            print('该公司最近一个月有招聘')
        else:
            print(isnull)
        if jobs_list and len(isnull)!=1:
            for job in jobs_list:
                job_url = job.xpath('./p/span/a/@href')
                if job_url:
                    print(job_url[0])
                    job_url = job_url[0]
                    print(job_url)
                    if not self.myredis.sismember(self.table[0], job_url):
                        yield scrapy.Request(job_url,
                                             headers=self.headers,
                                             callback=self.get_detail,
                                             meta={'jobterm':jobterm,
                                                   "source_url":response.url},
                                             dont_filter=True)

        else:
            print('近一个月没有找到相关招聘')


        is_next = html_list.xpath('//a[contains(text(),"下一页")]/@href')

        if is_next:
            next_page = is_next[0]
            print('next page',next_page)
            yield scrapy.Request(next_page,headers=self.headers,dont_filter=True)

    #爬取明细页面
    def get_detail(self,response):
        url = response.url
        source_url = response.meta['source_url']
        jobterm=response.meta['jobterm']
        position = ''
        salary = ''
        company = ''
        jobtxt=''
        com_people = ''
        com_cate = ''
        com_profession = ''
        district = ''
        experience = ''
        people = ''
        posttime = ''
        city = ''
        jobtag = ''
        jobcate = ''
        keyword = ''
        address = ''
        job_demand = ''
        introduction = ''
        degree = ''
        hash_id=''
        Insert_database_time=''

        html_ = response.text
        html = etree.HTML(html_)
        position = html.xpath('//h1/@title') if html.xpath('//h1/@title') else ''
        salary = html.xpath('//div[@class="cn"]//strong/text()') if html.xpath(
            '//div[@class="cn"]//strong/text()') else ''
        company = html.xpath('//p[@class="cname"]/a[1]/@title') if html.xpath(
            '//p[@class="cname"]/a[1]/@title') else ''

        i = html.xpath('//div[@class="com_tag"]/p[1]/@title')
        if i:
            com_cate = [(x if x in i[0] else '') for x in
                        ['民营', '国企', '外资', '合资', '外企', '政府机关', '事业', '非营利', '上市', '创业']]
            if len("".join(com_cate)) >= 1:
                com_cate = i

        i = html.xpath('//div[@class="com_tag"]/p[2]/@title')
        if i:
            com_people = i[0] if "人" in i[0] else ''

        i = html.xpath('//div[@class="com_tag"]/p[3]/a')
        if i:
            com_profession = html.xpath('//div[@class="com_tag"]/p[3]/@title')[0]

        desciption = html.xpath('//p[@class="msg ltype"]/@title')
        if desciption:
            job_summery = "".join(desciption).split('|')
            city_ = job_summery[0].strip() if job_summery else ''
            if '-' in city_:
                city = city_.split('-')[0]
                district = city_.split('-')[1]
            else:
                city = city_
            for i in job_summery:
                if '经验' in i:
                    experience = i.strip()
                if '招' in i and '人' in i:
                    people = i.strip()
                if '发布' in i:
                    origin = ''.join(''.join(i).split())
                    post = origin.split('发布')[0]
                    now_month= int(str(datetime.datetime.now())[5:7])
                    if len(post.split('-')) == 2:
                        if int(post.split('-')[0])>=1 and int(post.split('-')[0])<=now_month:
                            posttime = str(datetime.datetime.now())[0:4]+'-'+post
                        else:
                            posttime= str(int(str(datetime.datetime.now())[0:4])-1)+'-'+post
                    else:
                        posttime=post
                di = "".join([x if x in i else '' for x in ['初中', '中专', '中技', '高中', '大专', '本科', '硕士', '博士']])
                if len(di) >= 1:
                    degree = i
                    print('degree', degree)
        else:
            job_summery=''

        jobtag = html.xpath('//div[@class="jtag"]/div//span/text()')
        jobcate = html.xpath('//div[@class="bmsg job_msg inbox"]/div/p[1]/a/text()')
        keyword = html.xpath('//div[@class="bmsg job_msg inbox"]/div/p[2]/a/text()')
        address = html.xpath('//div[@class="bmsg inbox"]/p/text()')
        job_demand = html.xpath('//div[@class="bmsg job_msg inbox"]//text()')
        introduction = html.xpath('//div[@class="tmsg inbox"]//text()')

        items = Job_51job_Item()
        items['source'] = '前程无忧'  # 来源
        items['url'] = ''.join(url).strip()  # 页面链接
        items['source_url'] = ''.join(source_url).strip()  # 搜索来源
        items['city'] = ''.join(city).strip()  # 城市
        items['district'] = ''.join(district).strip()  # 地区
        items['jobterm'] = ''.join(jobterm).strip()  # 职位类别
        items['position'] = ''.join(position).strip()  # 岗位名称
        items['salary'] = ''.join(salary).strip()  # 待遇范围
        items['degree'] = ''.join(degree).strip()  # 学历要求
        items['experience'] = ''.join(experience).strip()  # 工作经验
        items['people'] = ''.join(people).strip()  # 招聘人数
        items['posttime'] = ''.join(posttime).strip()  # 发布时间
        items['jobtxt'] = ''.join(job_summery).strip()  # 招聘文本
        items['jobtag'] = ' | '.join(jobtag).strip()  # 岗位亮点
        items['job_demand'] = ''.join(job_demand).strip()  # 岗位要求
        items['company'] = ''.join(company).strip()  # 公司名称
        items['com_people'] = ''.join(com_people).strip()  # 公司规模
        items['com_cate'] = ''.join(com_cate).strip()  # 公司种类
        items['com_profession'] = ''.join(com_profession).strip()  # 公司行业
        items['introduction'] = ''.join(introduction).strip()  # 公司介绍
        items['address'] = ''.join(address).strip()  # 公司地址
        items['jobcate'] = ''.join(jobcate).strip()  # 岗位分类
        items['keyword'] = ''.join(keyword).strip()  # 岗位关键词
        names, values = zip(*items.items())
        hash_id= hashlib.md5(str(values).encode("utf8")).hexdigest()
        items['Insert_database_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())# 入库时间
        items['hash_id'] = hash_id # hash_id
        if len(items['company'])>1:
            yield items
