import html_helper as hh
from html_helper import HTMLPage
import website_connection as wc
import config

def splash_page(page_css=None):
	html = HTMLPage(page_css=page_css)
	html.add_body(hh.generate_navbar(logged_in=False, active="splash"))
	html.add_body(hh.generate_main_div("""
		<p>
			Welcome to Sm4shed, a new ladder system for Project M!
		</p>
		<p>
			Sm4shed comes with a complex matchmaking system based on rankings as well as a custom version of dolphin that jumps right into netplay and records match results, removing the barrier of having to coordinate with your opponent.
		</p>
		<p class="alert_text">
			This project is currently in <b>SUPER ALPHA</b>, so do not expect anything more than a testbed for right now.
		</p>
		<p>
			I will be posting a roadmap soon to let you know what is happening in terms of development
		</p>
		<p>
			To use sm4shed, download the installer for your operating system. If you dont see your operating system, then it is not supported yet sorry :(
		</p>
		<p style="color:red;">
			as always, <b>use a unique password</b> for your account.
		</p>
		<p>
			if you are a professional player, let me know so that I can authenticate you and reserve your username!
		</p>
		<p>
			<b>Thanks goes out to...</b><br>
				The Dolphin Development Team<br>
				The Project M Development Team<br>
				The Smash Community<br>
		</p>"""))
	return html.get_html()
def home_page(page_css=None):
	html = HTMLPage(page_css=page_css)
	html.add_body(hh.generate_navbar(logged_in=True, active="home"))
	html.add_body(hh.generate_main_div("""
			<p>
				Welcome to Sm4shed, a new ladder system for Project M!
			</p>
			<p>
				Sm4shed comes with a complex matchmaking system based on rankings as well as a custom version of dolphin that jumps right into netplay and records match results, removing the barrier of having to coordinate with your opponent.
			</p>
			<p class="alert_text">
				This project is currently in <b>SUPER ALPHA</b>, so do not expect anything more than a testbed for right now.
			</p>
			<p>
				I will be posting a roadmap soon to let you know what is happening in terms of development
			</p>
			<p>
				<b>Thanks goes out to...</b><br>
					The Dolphin Development Team<br>
					The Project M Development Team<br>
					The Smash Community<br>
			</p>"""))
	return html.get_html()
def register_page(fail_text=None, page_css=None):
	html = HTMLPage(page_css=page_css)
	html.add_body(hh.generate_navbar(logged_in=False, active="register"))
	html.add_body("""<div style="padding:10px; margin-top:10px; margin-left:auto; margin-right:auto; max-width:1000px; position:relative; top:0; margin-bottom:10px; left:0; ">
	<div style="padding:10px; background-color: #eeeeee; font-family:Helvetica, Arial; font-weight:500; font-size:32px; text-align:center;">""")
	if fail_text:
		html.add_body("<p>" + logged_in + "</p>")
	html.add_body("""<form action="/register" method="POST"> <center>
		<table style="text-align:right;">
			<tr>
				<td>preferred username</td>
				<td><input type="text" style="font-size:30px; width:200px;" name="username"></td>
			</tr>
			<tr>
				<td>email</td>
				<td><input type="text" style="font-size:30px; width:200px;" name="email"></td>
			</tr>
			<tr>
				<td>password</td>
				<td><input type="password" style="font-size:30px; width:200px;" name="password"></td>
			</tr>
		</table>
		<input type="submit" value="Submit">
	</form> <center>
	</div>
	</div>""")
	return html.get_html()
def login_page(page_css=None):
	html = HTMLPage(page_css=page_css)
	html.add_body(hh.generate_navbar(logged_in=False, active="login"))
	html.add_body(hh.generate_main_div("""<form action="/login" method="POST"> <center>
		<table style="text-align:right;">
			<tr>
				<td>username</td>
				<td><input type="text" style="font-size:30px; width:200px;" name="username"></td>
			</tr>
			<tr>
				<td>password</td>
				<td><input type="password" style="font-size:30px; width:200px;" name="password"></td>
			</tr>
		</table>
		<input type="submit" value="Submit">
	</form> <center>"""))
	return html.get_html()

def profile_page(player_dict, page_css=None):
	html = HTMLPage(page_css=page_css)
	html.add_body(hh.generate_navbar(logged_in=True, active="profile"))

	body = """<div style="text-align:center; font-family:Edo, Helvetica, Arial; font-size:30px; font-weight:700;">
	<div style="font-size:64px;">""" + str(player_dict.get("username", None)) + """</br></div>
	""" + str(player_dict.get("wins", 0)) + ' - ' + str(player_dict.get("losses", 0)) + ' - ' + str(player_dict.get("draws", 0)) + """</br>
	Desyncs: """ + str(player_dict.get("desyncs", 0)) + """</br>
	</div>"""


	html.add_body(hh.generate_main_div(body))
	return html.get_html()

def ranked_matchmaking_info_page(page_css=None):
	html = HTMLPage(page_css=page_css)
	html.add_body(hh.generate_navbar(logged_in=True, active="ranked"))

	body = """
		<h1 class="edo_header">
			Ranked Matchmaking
		</h1>
		<div>
			<b>Read all of this information before entering ranked matchmaking</b>
			<ul>	
				<li>ranked matchmaking only scores your first game
				<li>pausing is prohibited, in future versions there will be pausing penalties built in
				<li>exiting before the match is over will be counted as a desync and rage quitting will result in a loss in future versions
				<li>if a desync occurs, it will count for both players and the match will be thrown out, if you have too many desyncs occuring, considering debugging your system to find out what the problem is
				<li>you will have to modify your dolphin settings the first time your emulator starts, to do this, just change the settings after the emulator loads
				<li>quitting before the game has started will not count as a desync in future versions
			</ul>
			<b>when matching is complete and dolphin loads...</b>
			<ul>
				<li>if you are the host, set the buffer to be 1/17th the highest ping
				<li>change controls and use the netplay chat to discuss stage bans
				<li>host starts the game
				<li>go straight to Versus -> Fight
				<li>choose your characters and stage
				<li>play 1 4 stock match
			</ul>
			<b>after the match is over...</b>
			<ul>
				<li>let the results screen load and the matchmaking page on the lobby display the results before exiting the game.
				<li>queue up again
			</ul>
		</div>"""

	body += "<center>" + hh.create_smash_button(975, 100, 'rgb(255, 50, 10)', word='Ranked Matchmaking', new_window='/start_ranked', offset_up=10, button_type='full') + "</center>"

	html.add_body(hh.generate_main_div(body))

	return html.get_html()

def ranked_matchmaking_start(page_css=None):
	html = HTMLPage(page_css=page_css)

	html.add_header(hh.add_js("js/check_matchmaking.js"))

	html.add_body(hh.generate_navbar(logged_in=True, active="ranked"))

	html.add_body(hh.generate_main_div(
		"""<div id="wait_screen">
			Not Pinged Yet
		</div>
		<script>
			check_matchmaking();
		</script>"""
	))

	return html.get_html()
