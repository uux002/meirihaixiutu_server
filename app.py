import logging; logging.basicConfig(level=logging.INFO)
import asyncio, os, json, time
from datetime import datetime
from aiohttp import web
import hashlib


async def index(request):
	echostr = 'success'
	try:
		signature = request.query['signature']
		timestamp = request.query['timestamp']
		nonce = request.query['nonce']
		echostr = request.query['echostr']
		token = 'jkilopqcv0968'
		list = [token,timestamp,nonce]
		list.sort()
		sha1 = hashlib.sha1()
		map(sha1.update,list)
		hashcode = sha1.hexdigest()
		logging.info("handle/GET func: hashcode, signature:",hashcode,signature)
		if hashcode == signature:
			return echostr
		else:
			return ""
	except Exception as ex:
		return ex

	#return web.Response(body=echostr.encode('utf-8'))


	#resp = web.Response(body=b'<h1>Fuck you man</h1>')
	#resp.content_type = 'text/html;charset=utf-8'
	#return resp

async def postWX(request):
	pass

@asyncio.coroutine
def init(loop):
	app = web.Application(loop=loop)
	app.router.add_route('GET','/',index)
	app.router.add_route('POST','/',postWX)
	srv = yield from loop.create_server(app.make_handler(),'127.0.0.1',7000)
	logging.info('Server started at http://127.0.0.1:7000...')
	return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()