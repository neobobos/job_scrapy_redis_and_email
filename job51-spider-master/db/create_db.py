import pymysql
from config import MYSQL_DATA_DB,MYSQL_PORT,MYSQL_USER,MYSQL_PASSWD,MYSQL_CHARSET,MYSQL_HOST

# 填写你的sql语句
sql = """
CREATE TABLE `job_51job` (
  `Id` int(10) NOT NULL AUTO_INCREMENT,
  `source` varchar(100) DEFAULT '  ' COMMENT '来源',
  `company` varchar(100) DEFAULT '  ' COMMENT '公司名称',
  `url` varchar(2000) DEFAULT '  ' COMMENT '页面链接',
  `source_url` varchar(2000) DEFAULT '  ' COMMENT '搜索来源',
  `city` varchar(100) DEFAULT '  ' COMMENT '城市',
  `district` varchar(100) DEFAULT '  ' COMMENT '地区',
  `jobterm` varchar(100) DEFAULT '  ' COMMENT '职位类别',
  `position` varchar(100) DEFAULT '  ' COMMENT '岗位名称',
  `salary` varchar(100) DEFAULT '  ' COMMENT '待遇范围',
  `degree` varchar(100) DEFAULT '  ' COMMENT '学历要求',
  `experience` varchar(100) DEFAULT '  ' COMMENT '工作经验',
  `people` varchar(100) DEFAULT '  ' COMMENT '招聘人数',
  `posttime` varchar(100) DEFAULT '  ' COMMENT '发布时间',
  `jobtxt` varchar(150) DEFAULT '  ' COMMENT '招聘文本',
  `jobtag` varchar(100) DEFAULT '  ' COMMENT '岗位亮点',
  `job_demand` text COMMENT '岗位要求',
  `com_people` varchar(100) DEFAULT '  ' COMMENT '公司规模',
  `com_cate` varchar(100) DEFAULT '  ' COMMENT '公司种类',
  `com_profession` varchar(100) DEFAULT '  ' COMMENT '公司行业',
  `introduction` text COMMENT '公司介绍',
  `address` varchar(200) DEFAULT '  ' COMMENT '公司地址',
  `jobcate` varchar(100) DEFAULT '  ' COMMENT '岗位分类',
  `keyword` varchar(100) DEFAULT '  ' COMMENT '岗位关键词',
  `hash_id` varchar(50) DEFAULT '  ' COMMENT '去重哈希',
  `Insert_database_time` varchar(50) DEFAULT '  ' COMMENT '插入时间',
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
"""

# 连接mysql
connect  = pymysql.connect(MYSQL_HOST,MYSQL_USER,MYSQL_PASSWD,MYSQL_DATA_DB,charset=MYSQL_CHARSET,port=MYSQL_PORT)
cursor = connect.cursor()
cursor.execute(sql)
connect.commit()
cursor.close()
connect.close()