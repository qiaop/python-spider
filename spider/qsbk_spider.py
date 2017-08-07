#!/usr/bin/env python
# -*- coding:utf-8 -*-
from bs4 import BeautifulSoup
import urllib
import urllib2
from peewee import *

database = MySQLDatabase(database = "qsbk",user = "root",passwd = "",host = '',port = 3306)
#数据库的配置需要自己填写正确的配置
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
    content = CharField(default = "")
    laught = CharField(default = "")
    comment = CharField(default = "")

database.connect()
database.create_table(Author,safe=True)
database.create_table(Duanzi,safe=True)



class Spider:

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

    def getContentText(self,item):
        return item.find('a',{'class':'contentHerf'}).find('div',{'class':'content'}).span.text

    def getContent(self,html):
        soup = BeautifulSoup(html,"html.parser")
        content_list = soup.body.find('div',{'id':'content'}).div.find('div',{'id':'content-left'}).children
        for item in content_list:
            if item.name == 'div':
                authorInstance = Author()
                duanzi = Duanzi()
                try:
                    contentstr =  item.find('a',{'class':'contentHerf'}).find('div',{'class':'content'}).span.text.strip()
                    duanzi.content = contentstr
                except AttributeError,e:
                    print 'No Content AttributeError'

                authorObject = item.find('div',{'class':'author clearfix'})

                try:
                    avatar = authorObject.a.img
                    avatarImg = avatar.get('src')
                    authorName = avatar.get('alt')

                    authorInstance.name = authorName
                    authorInstance.img = avatarImg
                except AttributeError,e:
                    print 'No Img AttributeError'

                try:
                    gender = authorObject.div['class'][1]
                    age = authorObject.div.text

                    authorInstance.gender = gender
                    authorInstance.age = age
                except AttributeError:
                    print 'No div AttributeError'
                except TypeError:
                    print 'TypeError'

                stats = item.find('div',{'class':'stats'})

                if stats is not None:
                    laughtNumber =  stats.find('span',{'class':'stats-vote'}).i.text
                    comment = stats.find('span',{'class':'stats-comments'}).a.i.text

                    duanzi.laught = laughtNumber
                    duanzi.comment = comment

                    print contentstr
                    print avatarImg
                    print authorName
                    print laughtNumber
                    print comment
                duanzi.author = authorInstance
                authorInstance.save()
                duanzi.save()

spider = Spider()
for page in range(1，11):
    url = 'http://www.qiushibaike.com/text/page/'+str(page)
    html = spider.getHtml(url)
    spider.getContent(html)
