# -*- coding: utf-8 -*-

import scrapy

class Job_51job_Item(scrapy.Item):
    table_name = 'job_51job'
    source= scrapy.Field()#来源
    url = scrapy.Field()  # 页面链接
    source_url = scrapy.Field()  # 搜索来源
    city = scrapy.Field()  # 城市
    district = scrapy.Field()  # 地区
    jobterm = scrapy.Field()  # 职位类别
    position = scrapy.Field()  # 岗位名称
    salary = scrapy.Field()  # 待遇范围
    degree = scrapy.Field()  # 学历要求
    experience = scrapy.Field()  # 工作经验
    people = scrapy.Field()  # 招聘人数
    posttime = scrapy.Field()  # 发布时间
    jobtxt = scrapy.Field()  # 招聘文本
    jobtag = scrapy.Field()  # 岗位亮点
    job_demand = scrapy.Field()  # 岗位要求
    company = scrapy.Field()  # 公司名称
    com_people = scrapy.Field()  # 公司规模
    com_cate = scrapy.Field()  # 公司种类
    com_profession = scrapy.Field()  # 公司行业
    introduction = scrapy.Field()  # 公司介绍
    address = scrapy.Field()  # 公司地址
    jobcate = scrapy.Field()  # 岗位分类
    keyword = scrapy.Field()  # 岗位关键词
    Insert_database_time = scrapy.Field() # 入库时间
    hash_id = scrapy.Field()    # 哈希值


 

