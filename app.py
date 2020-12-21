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
			name, id = _basic_auth(request.headers['Authorization'])
			actor = identify_actor(game, int(id or 0))
			cmd = r['cmd']
			target = r['target'] if 'target' in r else None
			outcome = game.process_action(actor, cmd, target)
			return web.Response(text=json.dumps({'outcome': outcome}), content_type='text/json')
		except AssertionError as e:
			return web.Response(status=400, text=json.dumps({'error': dict(*e.args)}), content_type='text/json')

	@routes.put('/pref')
	async def update_pref(request):
		try:
			r = await request.json()
			outcome = {}
			name, id = _basic_auth(request.headers['Authorization'])
			clan = request.cookies['clan']
			actor = identify_actor(game, int(id or 0))
			if actor.name != name:
				actor.name = name
				outcome['name'] = name
			if actor.clan != clan:
				actor.clan = clan
				outcome['clan'] = clan
			return web.Response(text=json.dumps({'outcome': outcome}), content_type='text/json')
		except AssertionError as e:
			return web.Response(status=400, text=json.dumps({'error': dict(*e.args)}), content_type='text/json')

	@routes.get('/board')
	async def show_board(request):
		return web.Response(text=(game.board.json(indent=2) + '\n'))

	app.add_routes(routes)
	return app

def _basic_auth(auth_header):
	auth = .split('Basic ', 1)[1]
	u, p = b64decode(auth).split(b':', 1)
	return u.decode(), p

def identify_actor(game, name=None, id=None):
	return next(player for player in game.players if player.name == u or player.id == p)
