from aiohttp import web
from base64 import b64decode
import pathlib
from os import path
import json

async def game2app(game):

	app = web.Application()
	routes = web.RouteTableDef()
	pwd = pathlib.Path(__file__).parent.absolute()

	def needs_auth(validate=lambda request: identify_actor(game, *_basic_auth(request.headers['Authorization'])),
	               unauthResponse=lambda: web.Response(status=401, headers={'WWW-Authenticate': "Basic"}, text="Unauthorized")):
		"Decorator factory that produces decorators that return unauthResponse() if validate(request) fails, and pass through the request otherwise"
		def auth_wrapper(f):
			def _(request, *args, **kwargs):
				try:
					assert validate(request)
				except (AssertionError, KeyError):
					return unauthResponse()
				return f(request, *args, **kwargs)
			return _
		return auth_wrapper

	@routes.get('/')
	async def main_page(request):
		return web.FileResponse(path.join(pwd, 'srv', 'game.html'))
	@routes.get('/game.js')
	async def main_page(request):
		return web.FileResponse(path.join(pwd, 'srv', 'game.js'))
	@routes.get('/game.css')
	async def main_page(request):
		return web.FileResponse(path.join(pwd, 'srv', 'game.css'))
	@routes.get('/teams.css')
	async def main_page(request):
		return web.FileResponse(path.join(pwd, 'srv', 'teams.css'))
	@routes.get('/login')
	@needs_auth()
	async def login_page(request):
		return web.Response(status=302, headers={'location': f"."})

	@routes.post('/move')
	@needs_auth()
	async def handle_move(request):
		try:
			r = await request.json()
			name, id = _basic_auth(request.headers['Authorization'])
			actor = identify_actor(game, name=name, id=int(id or 0))
			cmd = r['cmd']
			target = r['target'] if 'target' in r else None
			outcome = game.process_action(actor, cmd, target)
			return web.Response(text=json.dumps({'outcome': outcome}), content_type='application/json')
		except AssertionError as e:
			return web.Response(status=400, text=json.dumps({'error': dict(*e.args)}), content_type='application/json')

	@routes.put('/pref')
	async def update_pref(request):
		try:
			outcome = {}
			name, id = _basic_auth(request.headers['Authorization'])
			clan = request.cookies['clan']
			actor = identify_actor(game, name=name, id=int(id or 0))
			if actor.name != name:
				actor.name = name
				outcome['name'] = name
			if actor.clan != clan:
				actor.clan = clan
				outcome['clan'] = clan
			return web.Response(text=json.dumps({'outcome': outcome}), content_type='application/json')
		except AssertionError as e:
			return web.Response(status=400, text=json.dumps({'error': dict(*e.args)}), content_type='application/json')

	@routes.get('/board')
	async def show_board(request):
		return web.Response(text=(game.board.json(indent=2) + '\n'), content_type='application/json')

	app.add_routes(routes)
	return app

def _basic_auth(auth_header):
	auth = auth_header.split('Basic ', 1)[1]
	u, p = b64decode(auth).split(b':', 1)
	return u.decode(), p

def identify_actor(game, name=None, id=None):
	try:
		return next(player for player in game.players if player.name == name or player.id == id)
	except StopIteration:
		raise KeyError(name)
