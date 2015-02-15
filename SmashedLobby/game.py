import re
from config import *
import subprocess
import time
import os
import website_connection as WC

class Game:
	
	received_game_id = False
	received_game = False
	reported_hosting = False
	in_game = False
	game_finished = False
	game_reported = False

	game_id = None
	is_hosting = False

	dolphin_path = DOLPHIN_PATH
	game_file_location = GAME_FILE_LOCATION

	def __init__(self):
		self.reset()

	def reset(self):
		self.received_game_id = False
		self.is_hosting = False
		self.reported_hosting = False
		self.in_game = False
		self.game_finished = False
		self.game_reported = False
		self.game_id = False

	def perform_state(self, username, session_id):
		# still waiting for a game
		if not self.received_game_id:

			# send a request to check if matchmaking is finished
			resp_dict = WC.check_matchmaking(username, session_id)
			if resp_dict.get("success", None) and resp_dict.get("game_ready", None):
				self.received_game_id = True
				self.game_id = resp_dict.get("game_id", None)
			return resp_dict
		
		# have game id but havent parsed game
		elif not self.received_game:
			if DEBUG and GAME_CLASS_DEBUG:
				print ("[Game Class] still waiting for matchmaking")

			# get the match details
			resp_dict = WC.get_match(username, session_id, self.game_id)
			if resp_dict.get("success", None):
				self.received_game = True
				host_str = resp_dict.get("host", None)
				self.is_hosting = resp_dict.get((host_str + "_username"), None) == username
			return resp_dict

		# hosting but havent started the game
		elif self.is_hosting and not self.reported_hosting:
			if DEBUG and GAME_CLASS_DEBUG:
				print ("[Game Class] hosting")

			# skip this step if we are testing submission
			if GAME_NO_DOLPHIN:
				WC.host_reply(username, session_id, self.game_id)
				self.in_game = True
				self.reported_hosting = True
				return {"success": True, "local_system": "GAME_NO_DOLPHIN Faked Host Reply"}

			# start the dolphin process in host mode
			subprocess.Popen([self.dolphin_path, '--gamestate=' + self.game_file_location, '-H'])
			self.in_game = True

			# wait for dolphin to repond
			game_hosting_path = \
				os.path.join(self.game_file_location, "ready_for_hosting.txt")
			print "[Server] - Searching in", game_hosting_path
			while not os.path.isfile(game_hosting_path):
				print "Have Not found"
				time.sleep(1)

			# report dolphin is ready to host

			WC.host_reply(username, session_id, self.game_id)
			self.reported_hosting = True
			return {"success": True, "local_system": "Hosting Game Started"}

		# connecting but not sure if host is ready
		elif not self.is_hosting and not self.in_game:
			if DEBUG and GAME_CLASS_DEBUG:
				print ("[Game Class] connecting")

			# get match details and check if host is ready
			resp_dict = WC.get_match(username, session_id, self.game_id)
			if resp_dict.get("success", None) and resp_dict.get("host_ready", False):

				# parse the ip address of the host
				host_str = resp_dict.get("host", None)
				ip_address = resp_dict.get(host_str + "_ip")

				# start the match
				if not GAME_NO_DOLPHIN:
					subprocess.Popen([self.dolphin_path, '-C', ip_address, '--gamestate=' + self.game_file_location])
				
				self.in_game = True

				# add an extra message to resp dict
				resp_dict["local_system"] = "Connecting Game Started"
				resp_dict["local_parsed_ip"] = ip_address
			return resp_dict

		# in game but game not reported
		elif self.in_game and not self.game_reported:
			if DEBUG and GAME_CLASS_DEBUG:
				print ("[Game Class] In Game") 

			if GAME_NO_DOLPHIN:
				score_dict = DEBUG_GAME_DICT
				print "***",WC.submit_match(username, session_id, self.game_id, score_dict),"***"
				self.game_reported = True
				self.game_finished = True
				score_dict["local_system"] = "GAME_NO_DOLPHIN pushed fake game"
				return score_dict

			# check if game scores exists
			game_score_path = \
				os.path.join(self.game_file_location, 'game_score.txt')

			print "Searching for game results:",game_score_path 
			if os.path.isfile(game_score_path):
				with open(game_score_path, 'r') as file_obj:
					player_1_line = file_obj.readline().split(",")
					player_2_line = file_obj.readline().split(",")

					score_dict = {
						"p1_stocks": player_1_line[1],
						"p1_char": player_1_line[2],
						"p2_stocks": player_2_line[1],
						"p2_char": player_2_line[2],
						# placeholder for map, because dolphin cant sense map just yet
						"map": "None",
					}

					# submit score
					print WC.submit_match(username, session_id, self.game_id, score_dict)
					self.game_reported = True
					self.game_finished = True	
				score_dict["local_system"] = "Found game score and sent"
				score_dict["local_dir_files"] = str(os.listdir(self.game_file_location))
				return score_dict
			else:
				return {"success": True, "local_system": "Game Not Finished"}
			
		elif self.game_reported:
			return {"success": True, "local_system": "Game Finished"}
		else:
			if DEBUG and GAME_CLASS_DEBUG:
				print ("[Game Class] bad game state")
			return {"success": False, "local_system": "Bad State"}

	def is_finished(self):
		return self.game_finished

if __name__ == "__main__":
	g = Game()
	
	g.game_id = "5ygOcV5oOATO7zpZP1ht"

	g.received_game_id = True
	g.received_game = True
	g.reported_hosting = True
	g.in_game = True
	g.game_finished = False
	g.game_reported = False


