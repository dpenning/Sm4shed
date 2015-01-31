import tornado.ioloop
import tornado.web
import json
import datetime

import config
import webpages
import website_connection as WC
from game import Game

static_game = Game()

def get_page_css_from_cookie(handler):
	page_color = handler.get_cookie("page_color")
	if page_color == 'night':
		return "css/night.css"
	if page_color == 'day':
		return "css/day.css"
	return "css/day.css"

class IndexHandler(tornado.web.RequestHandler):
	def get(self):
		page_css = get_page_css_from_cookie(self)
		username = self.get_cookie("username")
		session_id = self.get_cookie("session_id")

		if not username or not session_id:
			self.write(webpages.splash_page(page_css=page_css))
			return
		else:
			self.write(webpages.home_page(page_css))
			return
class MissingHandler(tornado.web.RequestHandler):
	def get(self):
		self.redirect('/')
		return
	def post(self):
		self.redirect('/')
		return

class RegisterHandler(tornado.web.RequestHandler):
	def get(self):
		page_css = get_page_css_from_cookie(self)
		fail = self.get_argument("failure", default=None)
		if fail:
			if fail == "taken":
				fail_text = "username already taken"
			elif fail == "malformed":
				fail_text = "one or more forms weren't filled out"
			elif fail == "bad_user":
				fail_text = "your username was not sturdy enough"
			elif fail == "bad_pass":
				fail_text = "your password was not sturdy enough"
			elif fail == "bad_email":
				fail_text = "your email is not correct"
			elif fail == "db":
				fail_text = "The database is chugging right now, give it some time before you retry"
			else:
				fail_text = "Uncaught error type, please report this!"
			self.write(webpages.register_page(fail_text=fail_text, page_css=page_css))
			return
		else:
			self.write(webpages.register_page(page_css=page_css))
			return
	def post(self):
		username = self.get_argument("username", default=None)
		email = self.get_argument("email", default=None)
		password = self.get_argument("password", default=None)

		if not username or not email or not password:
			self.redirect("/register?failure=malformed")
			return

		resp_dict = WC.register(username, email, password)

		if not resp_dict.get("success"):
			reason = resp_dict.get("reason")
			if reason == "username already taken":
				self.redirect("/register?failure=taken")
				return
			elif reason == "invalid credentials form":
				self.redirect("/register?failure=malformed")
				return
			elif reason == "failed insert":
				self.redirect("/register?failure=db")
				return
		self.redirect("/login")
		return
class LoginHandler(tornado.web.RequestHandler):
	def get(self):
		page_css = get_page_css_from_cookie(self)
		self.write(webpages.login_page(page_css=page_css))
		return
	def post(self):
		username = self.get_argument("username", default=None)
		password = self.get_argument("password", default=None)

		# if malformed just redirect to the get page
		if not username or not password:
			self.redirect("/login")
			return

		# login to the server
		resp_dict = WC.login(username, password)

		if resp_dict.get("success", False):
			self.set_cookie("username", username)
			self.set_cookie("session_id", resp_dict.get("session_id"))
			self.redirect("/")
			return

		self.redirect("/login")
		return
class LogoutHandler(tornado.web.RequestHandler):
	def get(self):
		username = self.get_cookie("username")
		session_id = self.get_cookie("session_id")

		if not username or not session_id:
			self.redirect('/')
			return

		self.clear_cookie("username")
		self.clear_cookie("session_id")
		WC.logout(username, session_id)
		self.redirect('/')
		return
	def post(self):
		self.redirect('/')
		return

class RankedMatchMakingHandler(tornado.web.RequestHandler):
	def get(self):
		page_css = get_page_css_from_cookie(self)
		username = self.get_cookie("username")
		session_id = self.get_cookie("session_id")
		if not username or not session_id:
			self.redirect('/')
			return
		
		self.write(webpages.ranked_matchmaking_info_page(page_css=page_css))		
class RankedMatchMakingPlayHandler(tornado.web.RequestHandler):
	def get(self):
		# check if logged in
		page_css = get_page_css_from_cookie(self)
		username = self.get_cookie("username")
		session_id = self.get_cookie("session_id")
		if not username or not session_id:
			self.redirect('/')
			return
		# first start the search for a game
		WC.search_matchmaking(username, session_id)
		self.write(webpages.ranked_matchmaking_start(page_css=page_css))

class CheckGameHandler(tornado.web.RequestHandler):

	def get(self):
		self.write(json.dumps({"success":False}))

	def post(self):
		username = self.get_cookie("username")
		session_id = self.get_cookie("session_id")
		if not username or not session_id:
			self.write(json.dumps({'local_system': 'failed cookies'}))
			return
		check_state_dict = static_game.perform_state(username, session_id)
		check_state_dict["system_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
		self.write(json.dumps(check_state_dict))

class CancelGameHandler(tornado.web.RequestHandler):

	def post(self):
		username = self.get_cookie("username")
		session_id = self.get_cookie("session_id")
		if not username or not session_id:
			self.write(json.dumps({'local_system': 'failed cookies'}))
			return
		resp_dict = WC.stop_matchmaking(username, session_id)
		self.write(json.dumps(resp_dict))

class ProfileHandler(tornado.web.RequestHandler):

	def get(self):
		# get player info from the website and display it on your page
		page_css = get_page_css_from_cookie(self)
		username = self.get_cookie("username")
		session_id = self.get_cookie("session_id")
		if not username or not session_id:
			self.redirect('/')
			return

		resp_dict = WC.get_player(username)
		if resp_dict.get("success"):
			self.write(webpages.profile_page(resp_dict, page_css=page_css))
		else:
			self.redirect('/404')
			return

application = tornado.web.Application([
	(r"/font/(.*)", tornado.web.StaticFileHandler, {'path': 'static/font/'}),
	(r"/js/(.*)", tornado.web.StaticFileHandler, {'path': 'static/js/'}),
	(r"/css/(.*)", tornado.web.StaticFileHandler, {'path': 'static/css/'}),
    (r"/", IndexHandler),
    (r"/404", MissingHandler),
    (r"/check", CheckGameHandler),
    (r"/cancel", CancelGameHandler),
    (r"/register", RegisterHandler),
    (r"/login", LoginHandler),
    (r"/logout", LogoutHandler),
    (r"/ranked", RankedMatchMakingHandler),
    (r"/start_ranked", RankedMatchMakingPlayHandler),
    (r"/profile", ProfileHandler),

    (r".*", MissingHandler),
])

if __name__ == "__main__":
    application.listen(config.LOBBYPORT)
    tornado.ioloop.IOLoop.instance().start()