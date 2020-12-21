from .game import Game
from .app import web, game2app

g = Game()
web.run_app(game2app(g))
