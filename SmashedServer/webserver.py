import sys

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient

import json
from bson import json_util
import datetime
import time

from config import *
import db_operations as DB
from rabbit_operations import RabbitOperator

from tornado.options import define, options
define("port", default=8888, help="run on the given port", type=int)


unranked_operator = RabbitOperator(UNRANKED_QUEUE_NAME)
ranked_operator = RabbitOperator(RANKED_QUEUE_NAME)

################################################################################
# Website extras -- all tested
################################################################################

class IndexHandler(tornado.web.RequestHandler):

	def get(self):
		self.write("just an API for now, working on a client")

	def post(self):
		self.get()

################################################################################
# Value Gets
################################################################################

class JSONPlayerHandler(tornado.web.RequestHandler):

	def post(self):
		username = self.get_argument("username")
		if not username:
			self.write({"success": False,
				"reason": "invalid username form"})
			return

		user = DB.get_player_by_username(username)
		if not user:
			self.write({"success": False,
				"reason": "no user by that username"})
			return
		else:

			#format the game for output to the user, dont give them all the info
			return_dict = {"success": True}
			leave_out_fields = ["password_hash", "_id"]
			for k in user:
				if k not in leave_out_fields:
					return_dict[k] = user[k]

			self.write(json.dumps(return_dict, default=json_util.default))
			return
class JSONGetMatchInfoHandler(tornado.web.RequestHandler):

	def post(self):
		username = self.get_argument('username')
		session_id = self.get_argument('session_id')

		if not username or not session_id:
			self.write({"success": False,
				"reason": "invalid credential form"})
			return

		if not DB.is_logged_in(username, session_id):
			self.write({"success": False,
				"reason":"incorrect/expired login credentials"})
			return

		game_id = self.get_argument('game_id')

		if not game_id:
			self.write({"success": False,
				"reason":"invalid game_id form"})
			return

		game = DB.get_game_by_id(game_id)

		if game == None:
			self.write({"success": False,
				"reason":"no game found by that id"})
			return

		#format the game for output to the user, dont give them all the info
		return_dict = {"success": True}
		leave_out_fields = ["_id"]
		for k in game:
			if k not in leave_out_fields and "game_state" not in k:
				return_dict[k] = game[k]

		self.write(json.dumps(return_dict, default=json_util.default))
		return
class JSONCheckLoggedInHandler(tornado.web.RequestHandler):
	def post(self):
		username = self.get_argument('username')
		session_id = self.get_argument('session_id')

		if not username or not session_id:
			self.write({"success": False,
				"reason": "invalid credential form"})
			return

		if not DB.is_logged_in(username, session_id):
			self.write({"success": False,
				"reason":"incorrect/expired login credentials"})
			return
		self.write({"success": True})
		return

################################################################################
# User Settings -- all tested
################################################################################

class JSONRegisterHandler(tornado.web.RequestHandler):

	def post(self):
		username = self.get_argument('username', default=None)
		password_hash = self.get_argument('password_hash', default=None)
		email = self.get_argument('email', default=None)

		if not username or not password_hash or not email:
			self.write({"success": False,
				"reason": "invalid credentials form"})
			return

		if DB.get_player_by_username(username) != None:
			self.write({"success": False,
				"reason": "username already taken"})
			return

		if not DB.register_player(username, password_hash, email):
			self.write({"success": False,
				"reason": "failed insert"})
			return

		self.write({"success": True})
		return
class JSONLoginHandler(tornado.web.RequestHandler):

	def post(self):
		username = self.get_argument('username')
		password_hash = self.get_argument('password_hash')

		# if not valid login arguements, a false success
		if not username or not password_hash:
			self.write({"success": False,
						"reason": "invalid credential form"})
			return

		session_id = \
			DB.login_player(username, password_hash, self.request.remote_ip)

		print session_id

		if not session_id:
			self.write({"success": False,"reason": "invalid user/pass combo"})
			return

		self.write({"success": True, "session_id": session_id})
class JSONLogoutHandler(tornado.web.RequestHandler):

	def post(self):
		username = self.get_argument('username')
		session_id = self.get_argument('session_id')

		# if not valid login arguements, a false success
		if not username or not session_id:
			self.write({"success": False,
						"reason": "invalid credential form"})
			return

		self.write({"success": DB.logout_player(username, session_id)})

################################################################################
# Settings -- all tested
################################################################################

class JSONCharacterHandler(tornado.web.RequestHandler):

	def post(self):
		username = self.get_argument('username')
		session_id = self.get_argument('session_id')

		if not username or not session_id:
			self.write({"success": False,
						"reason": "invalid credential form"})
			return

		if not DB.is_logged_in(username, session_id):
			self.write({"success": False,
					"reason":"incorrect/expired login credentials"})
			return

		main_char = self.get_argument('main', "None")
		second_char = self.get_argument('second', "None")
		third_char = self.get_argument('third', "None")

		success = DB.change_main_character(usenrame, main_char) and \
		DB.change_second_character(usenrame, second_char) and \
		DB.change_third_character(usenrame, third_char)

		if not success:
			self.write({"success": False, "reason": "invalid characters"})
			return

		self.write({"success":True})

################################################################################
# Matchmaking -- all tested
################################################################################

class JSONAskMatchMakerStatusHandler(tornado.web.RequestHandler):
	def post(self):
		username = self.get_argument('username')
		session_id = self.get_argument('session_id')

		if not username or not session_id:
			self.write({"success": False,
						"reason": "invalid credential form"})
			return

		if not DB.is_logged_in(username, session_id):
			self.write({"success": False,
					"reason":"incorrect/expired login credentials"})
			return

		game_ready = DB.check_game_ready(username)
		if game_ready != None:
			game_id = game_ready.get("game_id", None)
			if game_id != None:
				DB.remove_game_ready(username)
				self.write({"success": True,
						"game_ready":True,
						"game_id": game_id})
				return
			else:
				self.write({"success": False,
					"reason":"game_id malformed"})
				return
		else:
			self.write({"success": True,
					"game_ready":False})
			return		

class JSONStartMatchMakerHandler(tornado.web.RequestHandler):
	def post(self):
		username = self.get_argument('username')
		session_id = self.get_argument('session_id')

		if not username or not session_id:
			self.write({"success": False,
				"reason": "invalid credential form"})
			return

		if not DB.is_logged_in(username, session_id):
			self.write({"success": False,
				"reason":"incorrect/expired login credentials"})
			return

		user = DB.get_player_by_username(username)
		rating = user.get("rating", 1000)

		if ranked_operator.insert_player_into_matchmaking_queue(
				username,rating):
			self.write({"success": True})
			return
		else:
			self.write({"success": False,
				"reason":"Failed insert"})
			return
class JSONStartUnrankedMatchMakerHandler(tornado.web.RequestHandler):
	def post(self):
		username = self.get_argument('username')
		session_id = self.get_argument('session_id')

		if not username or not session_id:
			self.write({"success": False,
				"reason": "invalid credential form"})
			return

		if not DB.is_logged_in(username, session_id):
			self.write({"success": False,
				"reason":"incorrect/expired login credentials"})
			return

		user = DB.get_player_by_username(username)
		rating = user.get("rating", 1000)

		if unranked_operator.insert_player_into_matchmaking_queue(
				username,rating):
			self.write({"success": True})
			return
		else:
			self.write({"success": False,
				"reason":"Failed insert"})
			return

class JSONStopMatchMakerHandler(tornado.web.RequestHandler):
	def post(self):
		username = self.get_argument('username')
		session_id = self.get_argument('session_id')

		if not username or not session_id:
			self.write({"success": False,
						"reason": "invalid credential form"})
			return

		if not DB.is_logged_in(username, session_id):
			self.write({"success": False,
					"reason":"incorrect/expired login credentials"})
			return

		if ranked_operator.remove_player_from_matchmaking_queue(username):
			self.write({"success": True})
			return
		else:
			self.write({"success": False,
				"reason":"Failed insert"})
			return
class JSONStopUnrankedMatchMakerHandler(tornado.web.RequestHandler):
	def post(self):
		username = self.get_argument('username')
		session_id = self.get_argument('session_id')

		if not username or not session_id:
			self.write({"success": False,
						"reason": "invalid credential form"})
			return

		if not DB.is_logged_in(username, session_id):
			self.write({"success": False,
					"reason":"incorrect/expired login credentials"})
			return

		if unranked_operator.remove_player_from_matchmaking_queue(username):
			self.write({"success": True})
			return
		else:
			self.write({"success": False,
				"reason":"Failed insert"})
			return

################################################################################
# Match -- Submit Match
################################################################################

class JSONHostMatchHandler(tornado.web.RequestHandler):

	def post(self):
		username = self.get_argument('username')
		session_id = self.get_argument('session_id')

		if not username or not session_id:
			self.write({"success": False,
						"reason": "invalid credential form"})
			return

		if not DB.is_logged_in(username, session_id):
			self.write({"success": False,
					"reason":"incorrect/expired login credentials"})
			return

		game_id = self.get_argument('game_id')

		if not game_id:
			self.write({"success": False,
				"reason":"invalid game_id form"})
			return

		if DB.host_match_ready(username, game_id):
			self.write({"success": True})
			return
		else:
			self.write({"success": False,
				"reason":"failed host notify"})
			return
class JSONSubmitMatchScorehandler(tornado.web.RequestHandler):

	def post(self):
		username = self.get_argument('username')
		session_id = self.get_argument('session_id')

		if not username or not session_id:
			self.write({"success": False,
						"reason": "invalid credential form"})
			return

		if not DB.is_logged_in(username, session_id):
			self.write({"success": False,
					"reason":"incorrect/expired login credentials"})
			return

		game_id = self.get_argument('game_id')

		p1_stocks = self.get_argument('p1_stocks')
		p2_stocks = self.get_argument('p2_stocks')

		p1_char = self.get_argument('p1_char')
		p2_char = self.get_argument('p2_char')

		game_map = self.get_argument('map')

		if not all([game_id, p1_stocks, p2_stocks, p1_char, p2_char, game_map]):
			self.write({"success": False,
						"reason": "invalid game_state form"})
			return

		if not DB.add_returned_game_state(username, game_id,
				{"p1_stocks" :p1_stocks,
				 "p2_stocks":p2_stocks, 
				 "p1_char": p1_char,
				 "p2_char": p2_char,
				 "map": game_map}):
			self.write({"success": False,
						"reason": "failed game state return"})
			return

		DB.check_game_fully_scored(game_id)
		self.write({"success": True})

################################################################################
# Main Website Functions
################################################################################


if __name__ == "__main__":
	tornado.options.parse_command_line()
	app = tornado.web.Application( handlers = [
		(r"/json/register", JSONRegisterHandler), # tested
		(r"/json/login", JSONLoginHandler),
		(r"/json/logout", JSONLogoutHandler),

		(r"/json/get/player", JSONPlayerHandler),
		(r"/json/get/match", JSONGetMatchInfoHandler),
		(r"/json/get/logged_in", JSONCheckLoggedInHandler),

		(r"/json/settings/character", JSONCharacterHandler),

		(r"/json/match/check", JSONAskMatchMakerStatusHandler),
		(r"/json/match/search", JSONStartMatchMakerHandler),
		(r"/json/match/stop", JSONStopMatchMakerHandler),
		(r"/json/match/submit", JSONSubmitMatchScorehandler),

		(r"/json/match/unranked_search", JSONStartUnrankedMatchMakerHandler),
		(r"/json/match/unranked_stop", JSONStopUnrankedMatchMakerHandler),

		(r"/json/match/host", JSONHostMatchHandler),

		(r"/", IndexHandler),
	])

	app.listen(8888)
	print "ready"
	tornado.ioloop.IOLoop.instance().start()

