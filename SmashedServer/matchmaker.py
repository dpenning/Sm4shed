from config import *
import json
import time
from Queue import Queue
import db_operations as DB
from bin_tree import BinTree
from rabbit_operations import RabbitOperator

class Matchmaker:

	def __init__(self, queue_name, game_type):
		self.rabbit_operater = RabbitOperator(queue_name)
		self.tree = BinTree()
		self.process_queue = Queue()
		self.current_users_dict = dict()
		self.game_type = game_type

	def remove_user(self, username):
		if username not in self.current_users_dict:
			print "Removing: Could Not Find", username
		if username in self.current_users_dict:
			print "Removing: Success", username
			rating = self.current_users_dict[username]
			del self.current_users_dict[username]
			self.tree.remove(rating, username)

	def parse_rabbit_message(self):
		preformed_message = self.rabbit_operater.check_insert_queue()
		if preformed_message == None:
			return False
		message = json.loads(preformed_message)
		print "*",message
		command = message.get("command", None)
		if command == "insert":
			username = message["username"]
			rating = message["rating"]
			if username not in self.current_users_dict:
				self.tree.insert(rating, username)
				self.current_users_dict[username] = message["rating"]
				self.process_queue.put((username, rating, MM_INITIAL_WIDTH))
			return True

		elif command == "remove":
			username = message["username"]
			self.remove_user(username)
			return True
		return False

	def perform_next_queue(self):
		if not self.process_queue.empty():
			next_process = self.process_queue.get()
			username = next_process[0]
			rating = next_process[1]
			width = next_process[2]

			if username not in current_users_dict:
				return False

			potential_matches = self.tree.all_pairs_inbetween(
				rating-width,
				rating+width)

			if len(potential_matches) > 1:
				min_distance = -1
				min_match = None
				for match in potential_matches:
					if match[1] != username:
						dist = abs(rating - match[0])
						if min_distance == -1 or \
								dist < min_distance:
							min_match = match
							min_distance = dist
				
				# insert game into the database
				print "Creating New Match", (username, min_match[1])

				DB.create_new_game(
					username,
					min_match[1],
					self.game_type)
				
				# remove from datastructures
				try:
					self.remove_user(username)
					self.remove_user(min_match[1])
				except Exception as e:
					print e
					print "Players:,", username, min_match[1]
					print "Failed to remove all player entries"
				return True

			else:
				# did not find match
				self.process_queue.put(
					(username, rating, width + MM_WIDTH_INCREMENT))
				return False

	def run(self):
		while True:
			if not self.parse_rabbit_message():
				time.sleep(MM_TICK_TIME)
				self.perform_next_queue()

if __name__ == "__main__":
	mm = Matchmaker(UNRANKED_QUEUE_NAME)
	mm.run()