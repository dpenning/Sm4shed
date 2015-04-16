from librabbitmq import Connection
from config import *
import json

class RabbitOperator:
	queue_name = None
	connection = None
	channel = None

	def __init__(self, qn):
		self.queue_name = qn
		self.connection = Connection()
		self.channel = self.connection.channel()
		self.start_matchmaking_queue()

	def start_matchmaking_queue(self):
		self.channel.queue_declare(queue=self.queue_name)

	def check_insert_queue(self):
		message = self.channel.basic_get(self.queue_name)
		if message:
			message.ack()
			return message.body
		else:
			return None

	def publish(self, body):
		try:
			self.channel.basic_publish(
				exchange='',
				routing_key=self.queue_name,
				body=json.dumps(body))
			return True
		except Exception as e:
			return False

	def insert_player_into_matchmaking_queue(self, username, rating):
		return self.publish({
			"command": "insert",
			"username": username,
			"rating": rating})
		
	def remove_player_from_matchmaking_queue(self, username):
		return self.publish({
			"command": "remove",
			"username": username})
