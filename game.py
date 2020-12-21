import random
import datetime
import itertools
import json

# https://www.youtube.com/watch?v=t9WMNuyjm4w

class Game():
	def __init__(self, n=3, interval=datetime.timedelta(days=1), board=None):
		if board is None:
			board = Board()
		elif not isinstance(board, Board):
			board = Board(**board)
		self.board = board
		self.interval = interval
		self.players = self.board._init_players([{'name': f"Player {i+1}", 'id': random.getrandbits(64)} for i in range(n)])

	async def aplay(self, actions_source, iter=True):
		while True:
			action = await actions_source.get()
			if action is None: break

			if iter:
				yield self.process_action(*action)
			else:
				self.process_action(*action)

	def play(self, actions_source, iter=True):
		for action in iter(actions_source):
			if action is None: break

			if iter:
				yield self.process_action(*action)
			else:
				self.process_action(*action)

	def process_action(self, actor, cmd, target=None):
		source = self.board.locate(actor)

		if cmd == 'collect':
			now = datetime.datetime.utcnow()
			assert actor.next_ap >= now, {'text': "Not ready yet"}

			print(f"{actor.name} collected")
			actor.next_ap = now + self.interval
			actor.ap += 1

			return actor.ap

		elif cmd == 'upgrade':
			assert actor.ap >= 1, {'text': "Insufficient AP"}

			print(f"{actor.name} upgraded")
			actor.ap -= 1
			actor.range += 1

			return actor.range

		elif cmd == 'move':
			assert actor.ap >= 1, {'text': "Insufficient AP"}

			dx = source[0] - target[0]
			dy = source[1] - target[1]

			assert 0 <= abs(dx) <= 1, {'text': "Can't move that far"}
			assert 0 <= abs(dy) <= 1, {'text': "Can't move that far"}
			assert abs(dx) + abs(dy) > 0, {'text': "Invalid move"}
			assert self.board.get(target) is None, {'text': "Destination occupied"}

			print(f"f{actor.name} moved ({dx:+},{dy:+})")
			actor.ap -= 1
			self.board.swap(source, target)

			return

		elif cmd == 'attack':
			assert actor.ap >= 1, {'text': "Insufficient AP"}

			victim = self.board.get(target)
			dx = source[0] - target[0]
			dy = source[1] - target[1]

			assert victim is not None, {'text': "Destination unoccupied"}
			assert max(abs(dx), abs(dy)) <= actor.range, {'text': "Target too far"}

			print(f"{actor.name} attacked {victim.name}")
			actor.ap -= 1
			victim.hp -= 1

			if victim.hp == 0:
				print(f"{victim.name}, died")
				self.board.set(target, None)

			return victim.hp

		elif cmd == 'gift':
			n = 1
			assert actor.ap >= n, "Insufficient AP"

			beneficiary = self.board.get(target)

			assert beneficiary is not None, {'text': "Destination unoccupied"}
			assert max(abs(dx), abs(dy)) <= actor.range, {'text': "Target too far"}

			print(f"{actor.name} sent {n} AP to {beneficiary.name}")
			actor.ap -= n
			beneficiary.ap += n

			return beneficiary.ap

		else:
			raise ValueError(f"Unrecognized action '{cmd}'")

class Player():
	def __init__(self, name, id, hp=3, ap=3, range=3, clan=None):
		self.name = name
		self.hp = hp
		self.ap = ap
		self.range = range
		self.next_ap = datetime.datetime.utcnow()
		self.id = id
		self.clan = clan

	def json(self):
		return json.dumps(self._obj())

	def _obj(self):
		return {
			'name':    self.name,
			'hp':      self.hp,
			'ap':      self.ap,
			'range':   self.range,
			'next_ap': self.next_ap.ctime(),
			'id':      self.id,
			'clan':    self.clan,
		}

class Board():
	def __init__(self, width=5, height=5):
		self._board = tuple(list(None for _ in range(width)) for _ in range(height))

	def _init_players(self, players):
		for player, (x, y) in zip(players, random.sample(list(itertools.product(range(len(self._board[0])), range(len(self._board)))), len(players))):
			self._board[y][x] = player

	def locate(self, player):
		for y, row in enumerate(self._board):
			for x, cell in enumerate(row):
				if cell is player:
					return (x, y)
		raise ValueError("Player not found.")

	def get(self, pos):
		return self._board[pos[1]][pos[0]]

	def set(self, pos, val):
		self._board[pos[1]][pos[0]] = val

	def swap(self, pos1, pos2):
		self._board[pos1[1]][pos1[0]], self._board[pos2[1]][pos2[0]] = self._board[pos2[1]][pos2[0]], self._board[pos1[1]][pos1[0]]

	def json(self, **opts):
		return json.dumps([[(cell._obj() if cell else None) for cell in row] for row in self._board], **opts)
