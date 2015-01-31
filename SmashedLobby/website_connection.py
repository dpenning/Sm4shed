import urllib2
from urllib import urlencode
import json
import hashlib
import time
import config


base_url = config.BASE_URL

def send_request(location, data):
	url = base_url + location
	data = urlencode(data)
	req = urllib2.Request(url, data)
	response = urllib2.urlopen(req)
	return json.loads(response.read())

def check_logged_in(username, session_id):
	output = send_request(
		'json/get/logged_in',
		{	
			"username":username ,
			"session_id":session_id,
		})
	return output.get('success', False)
def login(username, password):
	password_hash = hashlib.sha224(password).hexdigest()
	resp_dict = send_request(
		"json/login",
		{
			"username":username,
			"password_hash":password_hash
		})
	return resp_dict
def register(username, email, password):
	password_hash = hashlib.sha224(password).hexdigest()
	resp_dict = send_request(
		"json/register",
		{
			"username":username,
			"email":email,
			"password_hash":password_hash,
		})
	return resp_dict
def logout(username, session_id):
	resp_dict = send_request(
		"json/logout",
		{
			"username": username,
			"session_id": session_id,
		})
	return resp_dict
def host_reply(username, session_id, game_id):
	resp_dict = send_request(
		"json/match/host",
		{
			"username": username,
			"session_id": session_id,
			"game_id":game_id,
		})
	return resp_dict
def search_matchmaking(username, session_id):
	resp_dict = send_request(
		"json/match/search",
		{
			"username": username,
			"session_id": session_id,
		})
	return resp_dict
def check_matchmaking(username, session_id):
	resp_dict = send_request(
		"json/match/check",
		{
			"username": username,
			"session_id": session_id,
		})
	return resp_dict
def stop_matchmaking(username, session_id):
	resp_dict = send_request(
		"json/match/stop",
		{
			"username": username,
			"session_id": session_id,
		})
	return resp_dict
def get_match(username, session_id, game_id):
	resp_dict = send_request(
		"json/get/match", 
		{
			"username":username,
			"session_id":session_id,
			"game_id": game_id
		})
	return resp_dict
def submit_match(username, session_id, game_id, results):
	input_dict = {
		'username': username,
		'session_id': session_id,
		'game_id': game_id
		}
	for k, v in results.items():
		input_dict[k] = v

	resp_dict = send_request('json/match/submit', input_dict)
	return resp_dict
def get_player(username):
	resp_dict = send_request("json/get/player", {"username":username})
	return resp_dict
