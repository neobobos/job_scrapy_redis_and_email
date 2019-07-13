# 51job_scrapy_redis_mysql_toemail

#### 采用关键字或批量（mysql table）爬取，分布式获取，分代理与无代理双模式。（目标量大必须采用代理模式）

### 进入文件根目录运行： python run_email.py


#### [job_51job_url.py]核心配置参数
```
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

```
###### [run_mail.py]下函数run说明：
```
def run(web=True,email_=True): #web 默认开启网络爬虫，email_ True默认爬取完毕，发送邮件
    if web:
        os.system("cd e:/job51-spider-master && python3 job_51job_url.py") #e:/job51-spider-master为爬虫文件夹路径，需修改
    if email_:
        txt = get_data_from_db()
        print(txt)
        email_qq(txt)
run(web=True,email_=True)
```

### 爬取关键字定制：
```
#添加 ‘爬虫’两字为关键字，可以自定义设置
myredis.sadd(REDISKEY,"https://search.51job.com/list/040000,000000,0000,00,0,08,爬虫,2,1.html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=01")
```
### 大规模分布式爬取：
###### 关键词在mysql_table设置，加载URL到redis，可以大规模批量爬取
```
pur_url_redis(mysql_table, REDISKEY,spider_name) #参数分别为搜索关键字sql表，redis的start_urls ，爬虫名
```
### mysql redis 配置,运行前必须设置数据库与redis
```
MYSQL_HOST ='127.0.0.1'
MYSQL_USER = '****'  # 用户名
MYSQL_PASSWD = '****'  # 密码
MYSQL_PORT = 3306 
MYSQL_DATA_DB = '****'数据库名
MYSQL_CHARSET = 'utf8mb4'

REDIS_URL = 'redis://:@127.0.0.1:6379/10'
REDIS_HOST="127.0.0.1"
REDIS_PWD='' #无密码模式
REDIS_PORT=6379
REDIS_DB=10
```
