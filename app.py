import logging; logging.basicConfig(level=logging.INFO)
import asyncio, os, json, time
from datetime import datetime
from aiohttp import web
import hashlib


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
	reg = r'''<xml><ToUserName><!\[CDATA\[(.*?)\]\]></ToUserName>
	<FromUserName><!\[CDATA\[(.*?)\]\]></FromUserName>
	<CreateTime>(.*?)</CreateTime>
	<MsgType><!\[CDATA\[(.*?)\]\]></MsgType>'''
	ToUserName, FromUserName, CreateTime, MsgType = re.findall(reg, info)[0]

	result = 'success'
	if MsgType.lower() == 'text':
		msg = "主人，我爱你"
		return web.Response(body=msg.encode('utf-8'))
	elif MsgType.lower() == 'voice':
		pass
	elif MsgType.lower() == 'event':
		reg = r'''<Event><!\[CDATA\[(.*?)\]\]></Event>'''
		Event = re.findall(reg, info)[0]
        # hu 接收事件推送（关注、取消关注等等）
		if Event.lower() == 'subscribe':       # hu 用户关注事件
			msg = "欢迎来到每日害羞图"
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