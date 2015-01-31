from config import *
import website_connection as WC
from getpass import getpass
from game import Game
import datetime
import time

g_username = ""
g_session_id = ""

def pprint(d):
	print "-----------"
	if "success" in d:
		print "success : ",d["success"]
	for i in d:
		if i != "success":
			print i,":", d[i]
	print "-----------"

def display_help_message():
	print 	"----------\n" + \
			"USERNAME:" + str(g_username) + "\n" + \
			"SESSION_ID:" + str(g_session_id) + "\n" + \
			"l|login - login user\n" + \
			"r|register - register new user\n" + \
			"o|logout - logout current user\n" + \
			"m|ranked - search for a ranked match\n" + \
			"u|unranked - search for a unranked match\n" + \
			"g|game - get game state\n" + \
			"p|profile - get user profile by name\n" + \
			"h|help - display help screen\n" + \
			"-----_----"

def prompt():
	request = raw_input("> ")

	if request in ["l", "login"]:
		login_prompt()
	elif request in ["o", "logout"]:
		WC.logout(g_username, g_session_id)
	elif request in ["r", "register"]:
		register_prompt()
	elif request in ["m", "ranked"]:
		ranked()
	elif request in ["u", "unranked"]:
		unranked()
	elif request in ["g", "game"]:
		game_prompt()
	elif request in ["p", "profile"]:
		profile_prompt()
	elif request in ["h", "help"]:
		display_help_message()
	else:
		display_help_message()

def login_prompt():
	global g_username
	global g_session_id
	username = raw_input("username: ")
	password = getpass("password: ")

	resp_dict = WC.login(username, password)
	if not resp_dict.get("success", False):
		print "Login Failed"
		pprint(resp_dict)
	else:
		g_username = username
		g_session_id = resp_dict.get("session_id")
def register_prompt():
	u = raw_input("username: ")
	e = raw_input("email: ")
	p = getpass("password: ")
	resp_dict = WC.register(u, e, p)
	if not resp_dict.get("success", False):
		print "Registration Failed"
		pprint(resp_dict)
	else:
		print "Registration Success"
def profile_prompt():
	u = raw_input("username: ")
	pprint(WC.get_player(u))
def game_prompt():
	game_id = raw_input("game_id")
	pprint(WC.get_match(g_username, g_session_id, game_id))
def unranked():
	print "Not Implemented Yet"
def ranked():
	WC.search_matchmaking(g_username, g_session_id)
	game = Game()
	while True:
		if game.is_finished():
			game.reset()
			print "Game Finished"
			break
		print "--",datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"--"
		pprint(game.perform_state(g_username, g_session_id))
		time.sleep(1)

if __name__ == "__main__":
	try:
		while True:
			prompt()
	finally:
		WC.logout(g_username, g_session_id)
