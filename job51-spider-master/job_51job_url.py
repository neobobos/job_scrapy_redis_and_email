# -*- coding: utf-8 -*-

import os,sys
basepath=os.path.abspath(os.path.abspath(__file__)+'/../')
sys.path.append(os.path.abspath(__file__))
print(basepath)
sys.path.append(basepath)

from config import REDIS_DB,REDIS_PORT,REDIS_PWD,REDIS_HOST
from job51_spider.spiders.job_51job_spider import  Job_51job_Spider
import re
from config import MYSQL_PORT,MYSQL_CHARSET,MYSQL_DATA_DB,MYSQL_PASSWD,MYSQL_USER,MYSQL_HOST
import random
import time
import pymysql
import redis
myredis = redis.Redis(host=REDIS_HOST, password=REDIS_PWD, port=REDIS_PORT, db=REDIS_DB)

def pur_url_redis(mysql_table,REDISKEY,spider_name):
    # 连接mysql，查询表总数
    conn = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWD, MYSQL_DATA_DB, charset=MYSQL_CHARSET,
                           port=MYSQL_PORT)
    cur = conn.cursor()
    get_company_num_sql = 'select count(*) from %s;' % mysql_table
    cur.execute(get_company_num_sql)
    conn.commit()
    cur.close()
    conn.close()

    TOTAL_NUM = int(cur.fetchone()[0])
    print("总数",TOTAL_NUM)

    # 获取历史爬取进度值，如果存在，则继承，如果不存在，则删除redis相关爬虫数据，重新开始。
    # 连接redis
    myredis = redis.Redis(host=REDIS_HOST, password=REDIS_PWD, port=REDIS_PORT, db=REDIS_DB)
    current_progress = myredis.hget('@' + spider_name, 'old_current_progress')
    print(current_progress)
    if current_progress:
        current_progress=int(current_progress.decode('utf-8'))
        STARTING_VALUE = current_progress
    else:
        STARTING_VALUE = 0
    print("STARTING_VALUE", STARTING_VALUE)

    # 区间
    INTERVAL = 1000

    # 查询语句
    while STARTING_VALUE < TOTAL_NUM:
        # 连接mysql，获取4000数据后，关闭连接
        conn = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWD, MYSQL_DATA_DB, charset=MYSQL_CHARSET,
                               port=MYSQL_PORT)
        cur = conn.cursor()
        query_sql = 'select name from %s limit %s,%s;'%(mysql_table,STARTING_VALUE,INTERVAL)
        cur.execute(query_sql)
        conn.commit()
        tuples = cur.fetchall()
        cur.close()
        conn.close()
        #获得url后，往redis key中添加url list，每次4000
        for onedata in tuples:
            company = onedata[0]
            if company:
                for cate in ["01","02","03","04"]:
                    URL = "https://search.51job.com/list/000000,000000,0000,00,3,99,{},1,1.html?jobterm={}".format(company,cate)
                    print(URL)
                    myredis.sadd(REDISKEY,URL)
        #添加url的位置数打印，以便后续维护
        print("循环中的starting_value", STARTING_VALUE+INTERVAL)
        #添加当前进度到redis，为4000整数倍
        myredis.hset('@' + spider_name, 'current_progress', STARTING_VALUE*4)
        print('本次push url 完成')

        # 监控redis key url数量,剩余url数量低于1000，停止等待，若大于1000则持续等待
        while True:
            if myredis.scard(REDISKEY) < 1000:
                STARTING_VALUE += INTERVAL
                break
            else:
                time.sleep(2)

        #判定起始位置值是否超过总量，若没有则持续增加4000，否则退出增加url循环。
        if STARTING_VALUE > TOTAL_NUM:
            myredis.hset('@' + spider_name, 'current_progress', TOTAL_NUM*4)
            break


if __name__=="__main__":
    mysql_table = 'job_company'#要搜索的公司名称，提取自mysql表
    mysql_resuts = 'job_51job' #保存爬取结果的表
    redis_table = mysql_resuts #redis结果去重key
    REDISKEY = Job_51job_Spider.redis_key #redis url key
    spider_name = Job_51job_Spider.name #爬虫名称

    # 判断当前是否有残余的redis url list
    myredis.delete(REDISKEY)
    myredis.delete(redis_table)
    myredis.delete(spider_name + ":dupefilter")
    myredis.delete(spider_name + ":requests")

    #关键词为mysql_table，加载URL到redis，循环添加
    #pur_url_redis(mysql_table, REDISKEY,spider_name)

    #单独添加
    myredis.sadd(REDISKEY,"https://search.51job.com/list/040000,000000,0000,00,0,08,%25E7%2588%25AC%25E8%2599%25AB,2,1.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=01&companysize=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=22&dibiaoid=0&address=&line=&specialarea=00&from=&welfare=")
    #从此文件启动爬虫，也可以在start文件夹下启动
    start_path=os.path.abspath(os.path.abspath(basepath+'/start/'))
    sys.path.append(start_path)
    os.system("cd {} && python  job_51job_start.py".format(start_path))
