# python-spider
python爬虫实战入门（爬取糗事百科）


## 概要
作为学习python的第一个实战项目。主要功能是爬取糗事百科的文字段子，以及作者信息和点赞评论的数量，将这些数据存储到mysql上。


### 环境
 - virtualenv
 - pytnon2.7
 - mysql

#### 使用virtualenv
使用virtualenv是为了与系统的python环境区分开来，可以随意用pip安装一些模块而不会影响到系统的python环境。[这里](http://pythonguidecn.readthedocs.io/zh/latest/dev/virtualenvs.html)是一个virtualenv比较好的使用文档，可以参考一下，下面是virtualenv几个常用的命令。

`virtualenv -p /usr/local/bin/python3 --no-site-package env`

		-p选择python版本
		--no-site-package 不复制系统第三方包
		
`source env/bin/activate`激活环境
`deactivate `关闭环境
#### 使用mysql
mysql服务是安装在一台Ubuntu的阿里云服务器上的，在第一次使用mysql数据库的时候我们要简单配置一下，例如字符编码之类的。下面是一些命令以及简单配置。

1. 查看字符集设置

		mysql> show variables like 'collation_%';

		mysql> show variables like 'character_set_%';
	
2. 修改配置文件

 		vim /etc/mysql/my.cnf
 		
 	```
 	# - "~/.my.cnf" to set user-specific options.
	# 
	# One can use all long options that the program supports.
	# Run program with --help to get a list of available options and with
	# --print-defaults to see which it would actually understand and use.
	#
	# For explanations see
	# http://dev.mysql.com/doc/mysql/en/server-system-variables.html

	#
	# * IMPORTANT: Additional settings that can override those from this file!
	#   The files must end with '.cnf', otherwise they'll be ignored.
	#

	!includedir /etc/mysql/conf.d/
	!includedir /etc/mysql/mysql.conf.d/
	[client]
	default-character-set = utf8

	[mysqld]
	character_set_server = utf8
	collation-server = utf8_general_ci
	bind-address = 0.0.0.0
                          
 	
 	```
 上面的几个配置除了设置字符编码外，还有一个配置	`bind-address = 0.0.0.0`，是配置可以远程访问mysql服务。设置完字符编码可以重启一下mysql服务。
 	
 
 		/etc/init.d/mysql restart

3. 常用命令

		初始化root密码
		mysql>update user set password=PASSWORD(‘123456’) where User='root';
		
 		授权远程主机访问
 		mysql>GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '123456' WITH GRANT OPTION;
 		
 		查看数据库
 		mysql>show databases;
 		
 		切换数据库
 		mysql>use dbname;
 		
 		查看数据表
 		mysql>show tables;
### 主要模块

- urllib
- urllib2 
- beautifulsoup4==4.6.0
- peewee==2.10.1
- PyMySQL==0.7.11

这里推荐pip 豆瓣源 https://pypi.doubanio.com/simple，速度非常快。

## 核心代码介绍

### 获取html

创建一个类`Spider`，`getHtml`方法用来抓取HTML

```python
def getHtml(self,url = None):
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
    headers = { 'User-Agent' : user_agent }
    try:
        request = urllib2.Request(url,headers = headers)
        response = urllib2.urlopen(request)
        html =  response.read()
    except urllib2.URLError, e:
        if hasattr(e,"code"):
            print e.code
        if hasattr(e,"reason"):
            print e.reason
    return html

```
url默认参数是None，我们通过方法传递url进来。`user_Agent`是头部字段。函数返回值是完整的HTML。

### 解析html
解析html使用了常用的解析框架beautifulsoup4。主要的思路就是先找到我们需要的内容的html标签在哪个位置（用浏览器审查元素），然后使用bs4的api查找和获取html的标签。例如
![](http://www.codepeng.cn/images/post/python/python_spider.png)

部分代码：

```python
 def getContent(self,html):
     soup = BeautifulSoup(html,"html.parser")
     content_list = soup.body.find('div',{'id':'content'}).div.find('div',{'id':'content-left'}).children

```

### 将数据放入数据库
这一步使用peewee，可以先看一下peewee使用文档，还是很简单的。

```python
from peewee import *

database = MySQLDatabase(database = "qsbk",user = "root",passwd = "password",host = '0.0.0.0',port = 3306)
# 连接数据库的配置，数据库，用户名，密码，host，端口

class BaseModel(Model):
    class Meta:
        database = database

class Author(BaseModel):
    name = CharField(default = "")
    img = CharField(default = "")
    gender = CharField(default = "")
    age = CharField(default = "")

class Duanzi(BaseModel):
    author = ForeignKeyField(Author)
    #外键为作者
    content = CharField(default = "")
    laught = CharField(default = "")
    comment = CharField(default = "")

database.connect()
#建立连接
database.create_table(Author,safe=True)
database.create_table(Duanzi,safe=True)
#创建表的参数safe=True，表示如果表不存在的话创建表，如果改为False，那么如果表已经存在了就会抛出异常。

```

```
authorInstance = Author()
duanzi = Duanzi()
···
···
authorInstance.save()
duanzi.save()
#调用save方法保存数据到数据库


```
爬虫使用数据库最佳建议使用Mongodb等nosql数据库。
### 开始爬虫

```
spider = Spider()
html = spider.getHtml(url)
spider.getContent(html)

```
