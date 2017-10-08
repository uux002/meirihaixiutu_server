# coding=utf-8
#import importlib,sys
#importlib.reload(sys)
#sys.setdefaultencoding('utf-8')

import logging; logging.basicConfig(level=logging.INFO)
import asyncio, os, json, time
from datetime import datetime
from aiohttp import web
import hashlib
import xml.etree.ElementTree as ET
import time
import random

auto_text_reply = [
	'求你了老公,我不嘛',
	'人家以后再也不理你了啦!',
	'别这样啦，人家是个女孩子嘛!',
	'别这样啦，之前你不是这个样子的嘛!',
	'不嘛不嘛，我要我要',
	'人家就是想要你多关心一点!',
	'就要就要，人家就要，不给就不理你了',
	'你坏哦! 我要告诉妈妈说你欺负女孩子!',
	'你好讨厌哦!',
	'没人跟你一起啊! 我陪你吧!',
	'你今天有没有想念人家呀!',
	'人家不开心',
	'你好坏哦，欺负人家，哼!',
	'老公，帮我拎着包裹，你看人家的小手，都勒出红印来了',
	'老公，我累了，你去做饭吧，求求你了!',
	'看到你心情就特别好!',
	'一天没和你聊天，就觉得哪里不对劲!',
	'不要这样嘛!',
	'你才傻瓜呢!',
	'快亲亲人家啦!',
	'我家宝贝就这样，嘿嘿',
	'如果我不在这了，你会喜欢别的女孩么!',
	'想你想的睡不着',
	'别生气了，我错了还不行呀~'
]

def get_random_text_reply_content():
	count = len(auto_text_reply)
	selected_index = random.randint(0,count - 1)
	return auto_text_reply[selected_index]


def parse_xml(xmlData):
	ToUserName = xmlData.find('ToUserName').text
	FromUserName = xmlData.find('FromUserName').text
	CreateTime = xmlData.find('CreateTime').text
	MsgType = xmlData.find('MsgType').text
	#Content = xmlData.find('Content').text
	#MsgId = xmlData.find('MsgId').text
	#print(ToUserName,FromUserName,CreateTime,MsgType,Content,MsgId)
	return ToUserName,FromUserName,CreateTime,MsgType

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
	raw_xml = raw_xml.replace("时间戳",int(time.time()))
	return raw_xml



def index(request):
	echostr = 'success'
	try:
		echostr = request.query['echostr']
	except Exception as ex:
		pass

	logging.info("Echo STR:" + echostr)
	return web.Response(body=echostr.encode('utf-8'))

	#return web.Response(body=echostr.encode('utf-8'))


	#resp = web.Response(body=b'<h1>Fuck you man</h1>')
	#resp.content_type = 'text/html;charset=utf-8'
	#return resp

async def postWX(request):
	info = await request.text()
	logging.info("收到post请求:" + info)
	xmlData = ET.fromstring(info)
	ToUserName, FromUserName,CreateTime,MsgType = parse_xml(xmlData)
	
	result = 'success'
	if MsgType.lower() == 'text':
		content = get_random_text_reply_content()
		msg = get_text_reply_xml(FromUserName,ToUserName,content)
		return web.Response(body=msg.encode('utf-8'))
	elif MsgType.lower() == 'voice':
		pass
	elif MsgType.lower() == 'event':
		reg = r'''<Event><!\[CDATA\[(.*?)\]\]></Event>'''
		Event = re.findall(reg, info)[0]
        # hu 接收事件推送（关注、取消关注等等）
		if Event.lower() == 'subscribe':       # hu 用户关注事件
			msg = get_text_reply_xml(FromUserName,ToUserName,"主人，欢迎你来到每日害羞图，我会好好爱你的，嘿嘿")
			return web.Response(body=msg.encode('utf-8'))
		elif Event.lower() == 'unsubscribe':  # hu 取消关注事件
			pass
	
	return web.Response(body=result.encode('utf-8'))

@asyncio.coroutine
def init(loop):
	app = web.Application(loop=loop)
	app.router.add_route('GET','/wx',index)
	app.router.add_route('POST','/wx',postWX)
	srv = yield from loop.create_server(app.make_handler(),'127.0.0.1',7000)
	logging.info('Server started at http://127.0.0.1:7000...')
	return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()


