# coding=utf-8
#import importlib,sys
#importlib.reload(sys)
#sys.setdefaultencoding('utf-8')

import logging; logging.basicConfig(level=logging.INFO)
import asyncio, os, json, time
from datetime import datetime
from aiohttp import web
import aiohttp
import hashlib
import xml.etree.ElementTree as ET
import time
import random
import urllib
import ssl
import csv
import threading

article_config_lock = threading.Lock()
conversition_config_lock = threading.Lock()

article_config_file = "article_config.csv"
conversition_config_file = "conversiton.csv"

access_token = "DLJcm9xzAbeVy_71x96Bfo3riNhQFzM9msiQm9qc9PULO0_nhOfG4KcRTPUwA-UTdgHHZsGCirP1AkMy7kbkDpTDUWncViyMq0zQSt2HZeQSIZgAJAKAR"
images_list_get_url = "https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token="
test_img_url = 'https://mmbiz.qpic.cn/mmbiz_jpg/WS65rNlb1aqhNRcqLmFb3J3kJdtX73U7bphlGPVbl0u448q4rlBF3iayEKmxRGtMviaVWj3tjglHXpS86t0f23xg/0?wx_fmt=jpeg'

unpublic_article_list = []
public_article_list = []
auto_text_reply = []

class Article:
	def __init__(self, title,des, permanent_url, conver_url, public_date, public_symbol):
		self.title = title
		self.des = des
		self.permanent_url = permanent_url
		self.conver_url = conver_url
		self.public_date = public_date
		self.is_publiced = False
		if public_symbol.lower() == 'y':
			self.is_publiced = True

# 加载随机文本回复配置
def load_conversition_config_csv():
	csv_file = open(conversition_config_file,encoding='utf-8')
	csv_reader = csv.reader(csv_file)

	try:
		for row in csv_reader:
			if(len(row) > 0):
				auto_text_reply.append(row[0])
	finally:
		pass
	csv_file.close()

# 载入文章配置表
def load_article_config_csv():
	csv_file = open(article_config_file,encoding='utf-8')
	csv_reader = csv.reader(csv_file)
	index = -1

	try:
		for row in csv_reader:
			index = index + 1
			if index <= 0:
				continue

			title = row[0]
			des = row[1]
			permanent_url = row[2]
			conver_url = row[3]
			public_date = row[4]
			public_symbol = row[5]

			article = Article(title,des,permanent_url,conver_url,public_date,public_symbol)
			if not article.is_publiced:
				unpublic_article_list.append(article)
			else:
				public_article_list.append(article)
	finally:
		pass
	csv_file.close()

# 从已发布的文章中随机选择一篇推送给用户
def get_publiced_article_for_ramdom():
	count = len(public_article_list)
	selected_index = random.randint(0,count - 1)
	article = public_article_list[selected_index]
	return article


# 获取一个随机文本返回给用户
def get_random_text_reply_content():
	count = len(auto_text_reply)
	selected_index = random.randint(0,count - 1)
	msg = auto_text_reply[selected_index]
	return msg

# 解析用户发过来的xml
def parse_xml(xmlData):
	ToUserName = xmlData.find('ToUserName').text
	FromUserName = xmlData.find('FromUserName').text
	CreateTime = xmlData.find('CreateTime').text
	MsgType = xmlData.find('MsgType').text
	#Content = xmlData.find('Content').text
	#MsgId = xmlData.find('MsgId').text
	#print(ToUserName,FromUserName,CreateTime,MsgType,Content,MsgId)
	return ToUserName,FromUserName,CreateTime,MsgType

# 解析用户发来的文本xml
def get_text_reply_xml(ToUserName, FromUserName, Content):
	raw_xml = '''<xml>
<ToUserName><![CDATA[粉丝号]]></ToUserName>
<FromUserName><![CDATA[公众号]]></FromUserName>
<CreateTime>时间戳</CreateTime>
<MsgType><![CDATA[text]]></MsgType>
<Content><![CDATA[回复内容]]></Content>
</xml>'''
	raw_xml = raw_xml.replace("粉丝号",ToUserName)
	raw_xml = raw_xml.replace("公众号", FromUserName)
	raw_xml = raw_xml.replace("回复内容",Content)
	raw_xml = raw_xml.replace("时间戳",str(int(time.time())))
	return raw_xml

# 解析用户发来的图片xml
def get_image_reply_xml(ToUserName,FromUserName):
	raw_xml = '''<xml>
<ToUserName><![CDATA[粉丝号]]></ToUserName>
<FromUserName><![CDATA[公众号]]></FromUserName>
<CreateTime>时间戳</CreateTime>
<MsgType><![CDATA[image]]></MsgType>
<PicUrl><![CDAtA[图片地址]]></PicUrl>
</xml>'''
	raw_xml = raw_xml.replace("粉丝号",ToUserName)
	raw_xml = raw_xml.replace("公众号", FromUserName)
	raw_xml = raw_xml.replace("图片地址",test_img_url)
	raw_xml = raw_xml.replace("时间戳",str(int(time.time())))
	return raw_xml

# 获取一个图文回复xml
def get_image_and_text_reply_xml(ToUserName, FromUserName):
	article = get_publiced_article_for_ramdom()

	raw_xml = '''<xml>
<ToUserName><![CDATA[粉丝号]]></ToUserName>
<FromUserName><![CDATA[公众号]]></FromUserName>
<CreateTime>时间戳</CreateTime>
<MsgType><![CDATA[news]]></MsgType>
<ArticleCount>1</ArticleCount>
<Articles>
<item>
<Title><![CDATA[标题]]></Title> 
<Description><![CDATA[描述]]></Description>
<PicUrl><![CDATA[封面图片地址]]></PicUrl>
<Url><![CDATA[文章地址]]></Url>
</item>
</Articles>
</xml>'''
	raw_xml = raw_xml.replace("粉丝号",ToUserName)
	raw_xml = raw_xml.replace("公众号", FromUserName)
	raw_xml = raw_xml.replace("时间戳",str(int(time.time())))
	raw_xml = raw_xml.replace("标题", article.title)
	raw_xml = raw_xml.replace("描述", article.des)
	raw_xml = raw_xml.replace("封面图片地址",article.conver_url)
	raw_xml = raw_xml.replace("文章地址", article.permanent_url)
	return raw_xml




def index(request):
	echostr = 'success'
	try:
		echostr = request.query['echostr']
	except Exception as ex:
		pass

	logging.info("Echo STR:" + echostr)
	return web.Response(body=echostr.encode('utf-8'))

async def postWX(request):
	info = await request.text()
	logging.info("收到post请求:" + info)
	xmlData = ET.fromstring(info)
	ToUserName, FromUserName,CreateTime,MsgType = parse_xml(xmlData)

	content = get_random_text_reply_content()
	msg = get_text_reply_xml(FromUserName,ToUserName,content)
	
	result = 'success'
	if MsgType.lower() == 'text':
		#content = get_random_text_reply_content()
		#msg = get_text_reply_xml(FromUserName,ToUserName,content)
		return web.Response(body=msg.encode('utf-8'))
	elif MsgType.lower() == 'voice':
		#msg = get_image_reply_xml(FromUserName,ToUserName)
		msg = get_image_and_text_reply_xml(FromUserName,ToUserName)
		return web.Response(body=msg.encode('utf-8'))
	elif MsgType.lower() == 'event':
		event = xmlData.find('Event').text
        # hu 接收事件推送（关注、取消关注等等）
		if event.lower() == 'subscribe':       # hu 用户关注事件
			msg = get_text_reply_xml(FromUserName,ToUserName,"主人，欢迎你来到每日害羞图，我会好好爱你的，嘿嘿")
			#msg = get_image_reply_xml(FromUserName,ToUserName)
			return web.Response(body=msg.encode('utf-8'))
		elif event.lower() == 'unsubscribe':  # hu 取消关注事件
			pass
	
	return web.Response(body=msg.encode('utf-8'))

@asyncio.coroutine
def init(loop):
	app = web.Application(loop=loop)
	app.router.add_route('GET','/wx',index)
	app.router.add_route('POST','/wx',postWX)
	load_article_config_csv()
	load_conversition_config_csv()

	content = get_random_text_reply_content()
	msg = get_text_reply_xml("FredShao","MeiRiHaiXiuTu",content)
	print(msg)

	srv = yield from loop.create_server(app.make_handler(),'127.0.0.1',7001)
	logging.info('Server started at http://127.0.0.1:7001...')
	return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()


