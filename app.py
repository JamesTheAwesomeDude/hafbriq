from aiohttp import web
from base64 import b64decode
import json

async def game2app(game):

	app = web.Application()
	routes = web.RouteTableDef()

	@routes.get('/')
	async def main_page(request):
		return web.FileResponse('srv/game.html')
	@routes.get('/game.js')
	async def main_page(request):
		return web.FileResponse('srv/game.js')
	@routes.get('/game.css')
	async def main_page(request):
		return web.FileResponse('srv/game.css')
	@routes.get('/teams.css')
	async def main_page(request):
		return web.FileResponse('srv/teams.css')

	@routes.post('/move')
	async def handle_move(request):
		try:
			r = await request.json()
			actor = identify_actor(request, game)
			cmd = r['cmd']
			target = r['target'] if 'target' in r else None
			outcome = game.process_action(actor, cmd, target)
			return web.Response(text=json.dumps({'outcome': outcome}), content_type='text/json')
		except AssertionError as e:
			return web.Response(status=400, text=json.dumps({'error': dict(*e.args)}), content_type='text/json')

	@routes.get('/board')
	async def show_board(request):
		return web.Response(text=(game.board.json(indent=2) + '\n'))

	app.add_routes(routes)
	return app

def identify_actor(request, game):
	u, p = b64decode(request.headers['Authorization'].split('Basic ', 1)[1]).split(b':', 1)
	u = u.decode()
	p = int(p)
	return next(player for player in game.players if player.name == u and player.id = p)
