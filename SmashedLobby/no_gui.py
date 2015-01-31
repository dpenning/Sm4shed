import sys
import signal
import os
from getpass import getpass
import urllib2
from urllib import urlencode
import json
import shutil
import time
import hashlib
import subprocess

DEBUG = True

if DEBUG:
	base_url = "http://127.0.0.1:8888/"
else:
	base_url = 'www.sm4shed.com/'

dolphin_path   = "/Users/dpenning/Github/dolphin/gui_build/Binaries/Dolphin.app/Contents/MacOS/Dolphin"
game_tmp_file_path = "tmp";

global_username = ""
global_session_id = ""


def pprint(d):
	print "-----------"
	if "success" in d:
		print "success : ",d["success"]
	for i in d:
		if i != "success":
			print i,":", d[i]
	print "-----------"

def send_request(location, data):
	url = base_url + location
	data = urlencode(data)
	req = urllib2.Request(url, data)
	response = urllib2.urlopen(req)
	return json.loads(response.read())

def reset_tmp_file_path():
	#clear the tmp path
	if os.path.exists(game_tmp_file_path):
		shutil.rmtree(game_tmp_file_path)
	os.mkdir(game_tmp_file_path)

def login(uname=None, password=None):
	global global_username
	global global_session_id

	if uname == None:
		username = raw_input("username: ")
	else:
		username = uname
	if password == None:
		p = getpass("password: ")
	else:
		p = password
	password_hash = hashlib.sha224(p).hexdigest()
	print password_hash
	resp_dict = send_request("json/login", {"username":username , "password_hash":password_hash})
	session_id = resp_dict.get("session_id", "")
	pprint(resp_dict)

	global_username = username
	global_session_id = session_id

def register():
	u = raw_input("username: ")
	e = raw_input("email: ")
	p = getpass("password: ")
	password_hash = hashlib.sha224(p).hexdigest()
	resp_dict = send_request("json/register", {"username":u, "email":e, "password_hash":password_hash})
	pprint(resp_dict)

def logout():
	global global_username
	global global_session_id
	resp_dict = send_request("json/logout", {"username": global_username, "session_id": global_session_id})
	pprint(resp_dict)
	global_username = ""
	global_session_id = ""

def status():
	print "username   = ", global_username
	print "session_id = ", global_session_id

def host_game(game_id):
	reset_tmp_file_path()
	# spawn the hosting dolphin instance
	subprocess.Popen([dolphin_path, '--gamestate=' + game_tmp_file_path, '-H'])

	# send back message to say ready to connect
	send_request("json/match/host",{"username": global_username, "session_id": global_session_id, "game_id":game_id})

def connect_game(ip_address):
	reset_tmp_file_path()
	subprocess.Popen([dolphin_path, '-C', ip_address, '--gamestate=' + game_tmp_file_path])

def search_matchmaking():
	global global_username
	global global_session_id
	resp_dict = send_request("json/match/search", {"username": global_username, "session_id": global_session_id })
	pprint(resp_dict)

def check_matchmaking():
	global global_username
	global global_session_id
	resp_dict = send_request("json/match/check", {"username": global_username, "session_id": global_session_id })
	pprint(resp_dict)
	return resp_dict

def stop_matchmaking():
	global global_username
	global global_session_id
	resp_dict = send_request("json/match/stop", {"username": global_username, "session_id": global_session_id })
	pprint(resp_dict)

def quit():
	logout()
	sys.exit()

def get_user(u):
	resp_dict = send_request("json/get/player", {"username":u})
	pprint(resp_dict)

def get_match(game_id):
	global global_username
	global global_session_id
	resp_dict = send_request(
		"json/get/match", {
			"username":global_username,
			"session_id":global_session_id,
			"game_id": game_id})
	pprint(resp_dict)
	return resp_dict

def print_help_screen():
	print "================="
	print "search"
	print "status"
	print "player <player>"
	print "logout"
	print "login"
	print "quit"
	print "================="

def clear():
	os.clear()

def full_matchmaking_wait():
	game_id = ""
	search_matchmaking()
	while True:
		time.sleep(1)
		check_match = check_matchmaking()
		if check_match.get("success", False):
			if check_match.get("game_ready", False):
				game_id = check_match.get("game_id", None)
				break
	if not game_id:
		print "Failed Matchmaking"
		return
	print "Success on finding match"

	match = get_match(game_id)
	host = match.get(match.get("host","") + "_username", None) == global_username

	if host:
		print "Hosting"
		host_game(game_id)
	else:
		print "connecting to", match.get(match.get("host","") + "_ip", "")
		while True:
			time.sleep(1)
			match = get_match(game_id)
			if match.get("host_ready", False):
				print "Starting Game with", match.get(match.get("host","") + "_username", None)
				connect_game(match.get(match.get("host","") + "_ip", ""))
				break

	# wait till we see game_score.txt
	


if __name__ == "__main__":
	reset_tmp_file_path()

	while True:
		command = raw_input("> ")
		if "quit" == command[:4]:
			quit()
		elif "player" == command[:6]:
			username = command[6:].strip()
			get_user(username)
		elif "game" == command[:4]:
			game_id = command[4:].strip()
			get_match(game_id)
		elif "login" == command.strip():
			login()
		elif "status" == command.strip():
			status()
		elif "register" == command.strip():
			register()
		elif "logout" == command.strip():
			logout()
		elif "search" == command.strip():
			search_matchmaking()
		elif "stop" == command.strip():
			stop_matchmaking()
		elif "matchmaking" == command.strip():
			full_matchmaking_wait()
		elif "check" == command.strip():
			check_matchmaking()
		elif "get_match" == command.strip():
			get_match("5ygOcV5oOATO7zpZP1ht")
		else:
			print_help_screen()
