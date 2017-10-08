# coding=utf-8
#import importlib,sys
#importlib.reload(sys)
#sys.setdefaultencoding('utf-8')

import logging; logging.basicConfig(level=logging.INFO)
import asyncio, os, json, time
from datetime import datetime
from aiohttp import web
import hashlib
import re
import xml.etree.ElementTree as ET

def parse_xml(xmlData):
	ToUserName = xmlData.find('ToUserName').text
	FromUserName = xmlData.find('FromUserName').text
	CreateTime = xmlData.find('CreateTime').text
	MsgType = xmlData.find('MsgType').text
	Content = xmlData.find('Content').text
	MsgId = xmlData.find('MsgId').text
	#print(ToUserName,FromUserName,CreateTime,MsgType,Content,MsgId)
	return ToUserName,FromUserName,CreateTime,MsgType,Content,MsgId

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
	ToUserName, FromUserName,CreateTime,MsgType,Content,MsgId = parse_xml(xmlData)

	result = 'success'
	if MsgType.lower() == 'text':
		msg = get_text_reply_xml(FromUserName,ToUserName,"主人，我爱你噢")
		return web.Response(body=msg.encode('utf-8'))
	elif MsgType.lower() == 'voice':
		pass
	elif MsgType.lower() == 'event':
		reg = r'''<Event><!\[CDATA\[(.*?)\]\]></Event>'''
		Event = re.findall(reg, info)[0]
        # hu 接收事件推送（关注、取消关注等等）
		if Event.lower() == 'subscribe':       # hu 用户关注事件
			msg = get_text_reply_xml(FromUserName,ToUserName,"主人，欢迎你来到每日害羞图")
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


