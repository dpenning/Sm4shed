import pymongo
import datetime
import random
import string
from math import exp

client = pymongo.MongoClient('localhost', 27017)

player_db = client["player_db"]
all_player_col = player_db["player_collection"]
logged_in_player_col = player_db["logged_in_player_collection"]

game_db = client["game_db"]
unresolved_games_col = game_db["unresolved_games_col"]

matchmaking_db = client["matchmaking_db"]
ready_col = matchmaking_db["ready_col"]

character_set = {
	"Wario",
	"Mario",
	"Luigi",
	"Peach",
	"Bowser",
	"Yoshi",
	"Donkey Kong",
	"Diddy Kong",
	"Captain Falcon",
	"Wolf",
	"Fox",
	"Falco",
	"Ice Climbers",
	"Zelda",
	"Sheik",
	"Link",
	"Toon Link",
	"Ganondorf",
	"Mewtwo",
	"Lucario",
	"Pikachu",
	"Jigglypuff",
	"Squirtle",
	"Ivysaur",
	"Charizard",
	"Samus",
	"Zero Suit Samus",
	"Lucas",
	"Ness",
	"Pit",
	"Kirby",
	"Meta Knight",
	"Dedede",
	"Ike",
	"Marth",
	"Roy",
	"Olimar",
	"Rob",
	"Mr. Game & Watch",
	"Snake",
	"Sonic",
	"None"}


################################################################################
# MongoDB setup
# ensure indexes for searching
################################################################################

all_player_col.ensure_index(
	[("username", pymongo.ASCENDING), ("unique", True), ("dropDups" , True)])
logged_in_player_col.ensure_index(
	[("username", pymongo.ASCENDING), ("unique", True), ("dropDups" , True)])

unresolved_games_col.ensure_index(
	[("game_id", pymongo.ASCENDING), ("unique", True), ("dropDups" , True)])
ready_col.ensure_index(
	[("username", pymongo.ASCENDING), ("unique", True), ("dropDups" , True)])


################################################################################
# Supporting Functions
################################################################################

# returns a session_id
def create_session_id():
	return ''.join(
		random.choice(
			string.ascii_lowercase + \
			string.ascii_uppercase + \
			string.digits) for _ in range(20))


################################################################################
# check if player is in database
################################################################################

# returns a player row or None
def get_player_by_username(username):
	return all_player_col.find_one({"username": username})

# returns a player row or None
def get_player_by_email(email):
	return all_player_col.find_one({"email": username})

def number_of_users():
	return all_player_col.count()

################################################################################
# Register a player into the db
################################################################################

# returns a boolean of success
def register_player(username, password_hash, email):

	new_player = {
		"username": username,
		"password_hash": password_hash,
		"email": email,
		"wins": 0,
		"losses": 0,
		"draws": 0,
		"desyncs": 0,
		"games_played": 0,
		"rating": 1000,
		"main_char": "None",
		"second_char": "None",
		"third_char": "None",
		"verified": False,
		"pro": False,
		"admin": False,
		"created_account": datetime.datetime.utcnow()
	}
	try:
		all_player_col.insert(new_player)
	except Exception as e:
		return False
	return True

# remove a player from the database
def remove_player(username):
	all_player_col.remove({"username": username})

################################################################################
# Login a player
################################################################################

# returns a boolean if fail and session_id if pass
def login_player(username, password_hash, ip_address):
	player = get_player_by_username(username)
	if player == None:
		return False

	if player["password_hash"] == password_hash:
		new_sid = create_session_id()
		logged_in_player = {
			"username": username,
			"last_command": datetime.datetime.utcnow(),
			"ip_address": ip_address,
			"session_id": new_sid
		}
		logged_in_player_col.update(
			{"username": username},
			logged_in_player,
			upsert=True)
		return new_sid

# returns a boolean of success
def logout_player(username, session_id):
	try:
		logged_in_player_col.remove({	"username":username,
										"session_id": session_id})
	except Exception as e:
		return False
	return True

################################################################################
# Check for login status
################################################################################

# returns boolean of success
def is_logged_in(username, session_id):
	return (logged_in_player_col.find_one(
		{"username": username, "session_id": session_id}) != None)

def get_logged_in_by_username(username):
	return logged_in_player_col.find_one({"username": username})


################################################################################
# Change Characters
################################################################################

# returns boolean of success
def change_main_character(username, new_main):
	if new_main == "None":
		return False
	if not new_main in character_set:
		return False
	try: 
		all_player_col.update(
			{"username": username},
			{"$set": {"main_char": new_main}})
		return True
	except Exception as e:
		return False

# returns boolean of success
def change_second_character(username, new_second):
	if not new_second in character_set:
		return False
	try: 
		all_player_col.update(
			{"username": username},
			{"$set": {"second_char": new_second}})
		return True
	except Exception as e:
		return False

# returns boolean of success
def change_third_character(username, new_third):
	if not new_third in character_set:
		return False
	try: 
		all_player_col.update(
			{"username": username},
			{"$set": {"third_char": new_third}})
		return True
	except Exception as e:
		return False


################################################################################
# Ranking and Score Updating
################################################################################

#returns new elo rank
def calc_new_rating(ply_r, opp_r, score, a=1000.0, k=100.0):
	expected_score = 1 / (exp(float(opp_r) - float(ply_r)) + 1)
	return float(ply_r) + (k * (score - expected_score))

def update_player_after_win(username, opponent):
	user = get_player_by_username(username)
	if user == None:
		return False

	opp = get_player_by_username(opponent)
	if opp == None:
		return False	
	try:
		new_rating = calc_new_rating(
			user.get("rating", 1000),
			opp.get("rating", 1000),
			1.0)
		wins = int(user.get("wins", 0))
		gp = int(user.get("games_played", 0))
		all_player_col.update(
			{"username": username},
			{"$set": {
				"wins": wins + 1,
				"rating": new_rating,
				"games_played": gp + 1}})
		return True
	except Exception as e:
		return False

def update_player_after_loss(username, opponent):
	user = get_player_by_username(username)
	if user == None:
		return False

	opp = get_player_by_username(opponent)
	if opp == None:
		return False	
	try:
		new_rating = calc_new_rating(
			user.get("rating", 1000),
			opp.get("rating", 1000),
			0.0)
		wins = int(user.get("wins", 0))
		gp = int(user.get("games_played", 0))
		all_player_col.update(
			{"username": username},
			{"$set": {
				"losses": wins + 1,
				"rating": new_rating,
				"games_played": gp + 1}})
		return True
	except Exception as e:
		return False

def update_player_after_draw(username, opponent):
	user = get_player_by_username(username)
	if user == None:
		return False

	opp = get_player_by_username(opponent)
	if opp == None:
		return False	
	try:
		new_rating = calc_new_rating(
			user.get("rating", 1000),
			opp.get("rating", 1000),
			0.5)
		wins = int(user.get("wins", 0))
		gp = int(user.get("games_played", 0))
		all_player_col.update(
			{"username": username},
			{"$set": {
				"draws	": wins + 1,
				"rating": new_rating,
				"games_played": gp + 1}})
		return True
	except Exception as e:
		return False

# update the player after a desync
def update_player_after_desync(username):
	user = get_player_by_username(username)
	if user == None:
		return False
	try:
		desyncs = int(user.get("desyncs", 0))
		gp = int(user.get("games_played", 0))
		all_player_col.update(
			{"username": username},
			{"$set": {
				"desyncs": desyncs + 1,
				"games_played": gp + 1}})
		return True
	except Exception as e:
		return False


################################################################################
# Games Handling
################################################################################

# returns boolean of success
def is_game_id(game_id):
	return unresolved_games_col.find_one({"game_id": game_id}) != None

def get_game_by_id(game_id):
	return unresolved_games_col.find_one({"game_id": game_id})

# returns None if failed, and gameid if success
def create_new_game(playername_1, playername_2, game_type):
	player_1 = get_player_by_username(playername_1)
	player_2 = get_player_by_username(playername_2)

	player_1_login = get_logged_in_by_username(playername_1)
	player_2_login = get_logged_in_by_username(playername_2)

	if player_1 == None or \
			player_2 == None or \
			player_1_login == None or \
			player_2_login == None or \
			"ip_address" not in player_1_login or \
			"ip_address" not in player_2_login:
		return None

	try:
		game_id = ""
		# try to get a valid game id
		while True:
			game_id = create_session_id()
			if not is_game_id(game_id):
				break

		# insert the game into the unresolved collection
		unresolved_games_col.insert(
			{
				"game_id": game_id,
				"time": datetime.datetime.utcnow(),
				"host": "p1",
				"host_ready": False,
				"p1_username": playername_1,
				"p1_rating": player_1.get("rating", 1000),
				"p1_ip": player_1_login["ip_address"],
				"p1_game_started": False,
				"p1_game_returned": False,
				"p1_game_state_p1_stocks":0,
				"p1_game_state_p2_stocks":0,
				"p1_game_state_p1_character":0,
				"p1_game_state_p2_character":0,
				"p1_game_state_map":"",

				"p2_username": playername_2,
				"p2_rating": player_2.get("rating", 1000),
				"p2_ip": player_2_login["ip_address"],
				"p2_game_started": False,
				"p2_game_returned": False,
				"p2_game_state_p1_stocks":0,
				"p2_game_state_p2_stocks":0,
				"p2_game_state_p1_character":0,
				"p2_game_state_p2_character":0,
				"p2_game_state_map":"",
			})
	except Exception as e:
		print e
		print "Create: Failed unresolved games insert"
		return None

	# add to the ready collection so the users can consume the game id and ip
	try:
		ready_col.update(
			{"username": playername_1}, {"$set": {"game_id":game_id}},
			upsert=True)
		ready_col.update(
			{"username": playername_2}, {"$set": {"game_id":game_id}},
			upsert=True)
	except Exception as e:
		print e
		print "Create: Failed Ready insert"
		return None

def start_game(username, game_id):
	game = get_game_by_id(game_id)
	if username == game["p1_username"]:
		unresolved_games_col.update(
			{"game_id": game_id},
			{"$set", {"p1_game_started": True}})
	elif username == game["p2_username"]:
		unresolved_games_col.update(
			{"game_id": game_id},
			{"$set", {"p2_game_started": True}})

# add the return state from a player to a game
def add_returned_game_state(username, game_id, game_state):
	# check if the game exists
	game = get_game_by_id(game_id)
	if game == None:
		print game, "Returned No Game"
		return False

	# check username to see which player user is
	pn = ""
	opn = ""
	if username == game.get("p1_username", None):
		pn = "p1"
		opn = "p2"
	elif username == game.get("p2_username", None):
		pn = "p2"
		opn = "p1"
	else:

		return False

	# add the game to the unresolved game state
	try:
		unresolved_games_col.update(
			{"game_id": game_id},
			{"$set": {
				pn + "_game_returned": True,
				pn + "_game_state_p1_stocks":game_state["p1_stocks"],
				pn + "_game_state_p2_stocks":game_state["p2_stocks"],
				pn + "_game_state_p1_character":game_state["p1_char"],
				pn + "_game_state_p2_character":game_state["p2_char"],
				pn + "_game_state_map":game_state["map"]
			}})
	except Exception as e:
		print "----------------------"
		print e
		print "----------------------"
		return False
	return True

def check_game_fully_scored(game_id):
	game = get_game_by_id(game_id)
	print "IN CHECK GAME"
	if game["p1_game_returned"] and game["p2_game_returned"]:
		if 	game["p1_game_state_p1_stocks"] == \
				game["p2_game_state_p1_stocks"] and \
				game["p1_game_state_p2_stocks"] == \
				game["p2_game_state_p2_stocks"]:
			# check for winning status
			if game["p1_game_state_p1_stocks"] > \
					game["p1_game_state_p2_stocks"]:
				print "P2 WIN"
				# p1 win p2 loss
				update_player_after_win(
					game["p1_username"], game["p2_username"])
				update_player_after_loss(
					game["p2_username"], game["p1_username"])
			elif game["p1_game_state_p1_stocks"] < \
					game["p1_game_state_p2_stocks"]:
				print "P1 WIN"
				# p1 win p2 loss
				update_player_after_loss(
					game["p1_username"], game["p2_username"])
				update_player_after_win(
					game["p2_username"], game["p1_username"])
			else:
				print "DRAW"
				# give draw for both
				update_player_after_draw(
					game["p1_username"], game["p2_username"])
				update_player_after_draw(
					game["p2_username"], game["p1_username"])
		else:
			print "DESYNC"
			# run the desync code for each player
			update_player_after_desync(game["p1_username"])
			update_player_after_desync(game["p2_username"])

		# reget game and store it in old games
		unresolved_games_col.update({"game_id": game_id},
			{"$set":
				{
				"p1_game_started": False,
				"p1_game_returned": False,
				"p1_game_state_p1_stocks":0,
				"p1_game_state_p2_stocks":0,
				"p1_game_state_p1_character":0,
				"p1_game_state_p2_character":0,
				"p1_game_state_map":"",

				"p2_game_started": False,
				"p2_game_returned": False,
				"p2_game_state_p1_stocks":0,
				"p2_game_state_p2_stocks":0,
				"p2_game_state_p1_character":0,
				"p2_game_state_p2_character":0,
				"p2_game_state_map":"",}})


# check if game is ready
def check_game_ready(username):
	return ready_col.find_one({"username": username})

def remove_game_ready(username):
	return ready_col.remove({"username": username})


# host match ready
def host_match_ready(username, game_id):
	game = get_game_by_id(game_id)
	if game == None:
		return False
	host_user = None
	if game["host"] == "p1":
		host_user = game["p1_username"]
	elif game["host"] == "p2":
		host_user = game["p2_username"]
	if username == host_user:
		unresolved_games_col.update(
			{"game_id": game_id},
			{"$set": {"host_ready": True}})
		return True
	return False




