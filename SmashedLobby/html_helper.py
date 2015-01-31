# html
def create_html(header, body):
	html = '<!DOCTYPE html>'
	html += '<html><head>' + header + '</head>'
	html += '<body>' + body + '</body>'
	html += '</html>'
	return html

# link
def add_ttf_font(location, name):
	html = '<style>'
	html += '@font-face {'
	html += 'font-family:' + name + ';'
	html += 'src: url(' + location + ') format(\'truetype\');'
	html += '}'
	html += '</style>'
	return html
def add_css(location):
	return '<link rel="stylesheet" type="text/css" href="' + location + '"/>'
def add_js(location):
	return '<script type="text/javascript" src="' + location + '"></script>'

# svg stuff
def add_title(title):
	return "<title>" + title + "</title>"
def add_style(style_dict):
	style = 'style="'
	for k, v in style_dict.items():
		style += str(k) + ':' + str(v) + '; '
	style += '"'
	return style
def create_circle(radius, cx, cy, color):
	html = '<circle r="' + str(radius) + '" '
	html += 'cx="' + str(cx) + '" '
	html += 'cy="' + str(cy) + '" '
	html += 'fill="' + str(color) +'" '
	html += '/>'

	return html
def create_polygon(points_list, color):
	html = '<polygon '
	html += 'points = "'
	for point in points_list:
		html += str(point[0]) + "," + str(point[1]) + " "
	html += '" '
	html += 'fill="' + str(color) + '" '
	html += '/>'
	return html
def create_smash_svg_text(word, offset_x, offset_y, size, text_length, color):
	# add the back layer, this provides the basis for the white stroke background
	html = '<text '
	html += 'text-anchor="start" '
	html += 'x="' + str(offset_x + 1) + '" '
	html += 'y="' + str(offset_y) + '" '
	html += 'textLength="' + str(text_length) + 'px" '
	html += 'fill="' + color + '" '
	html += 'font-family="Edo, Helvetica, Arial" '
	html += 'font-weight="700" '
	html += 'font-size="' + str(size) + 'px" '
	html += 'stroke="#ffffff" '
	html += 'stroke-width="5" '
	html += 'stroke-linecap="round"'
	html += '>'
	html += word
	html += '</text>'

	# add the forground, this provides the actual text in the correct color
	html += '<text '
	html += 'text-anchor="start" '
	html += 'x="' + str(offset_x) + '" '
	html += 'y="' + str(offset_y) + '" '
	html += 'textLength="' + str(text_length) + 'px" '
	html += 'fill="' + color + '" '
	html += 'font-family="Edo, Helvetica, Arial" '
	html += 'font-weight="700" '
	html += 'font-size="' + str(size) + 'px" '
	html += '>'
	html += word
	html += '</text>'
	return html
def create_smash_button(size_x, size_y, color, background_color = 'rgb(50, 50, 50)', word = None, float_val = None, button_type="standard", onclick=None, new_window=None, offset_up= 0, highlighted=False):
	outline_color = background_color
	shadow_color = background_color

	# for emphasis the shadow or outline is changed to the main color
	#if highlighted:
	#	shadow_color = color

	if highlighted:
		outline_color = color

	html = '<svg style="'
	if float_val:
		html += 'float: ' + float_val + ';'
	html += 'width: ' + str(size_x + 5) + 'px;'
	html += 'height: ' + str(size_y + 5) + 'px;'
	if onclick:
		html += '"><g onclick="window.location.href= \'' + onclick + '\'">'
	elif new_window:
		html += '"><g onclick="window.open(\'' + new_window + '\')">'
	else:
		html += '">'
	# draw button
	if button_type == "standard":
		# add shadow
		html += create_circle(size_y / 2, size_y / 2 + 5, size_y / 2 + 5, shadow_color)
		html += create_polygon([(size_y/2.0 + 5,0 + 5),(size_y/2.0 + 5,size_y + 5),(size_x * 3.0/4 + 5, size_y + 5),(size_x + 5, 0 + 5)], shadow_color)

		# add outline
		html += create_circle(size_y / 2, size_y / 2, size_y / 2, outline_color)
		html += create_polygon([(size_y/2.0,0),(size_y/2.0,size_y),(size_x * 3.0/4, size_y),(size_x, 0)], outline_color)

		# add background with color
		html += create_circle(size_y / 2 - 5, size_y / 2, size_y / 2, color)
		html += create_polygon([(size_y/2.0,5),(size_y/2.0,size_y-5),(size_x * 3.0/4 - 2, size_y-5),(size_x - 12, 5)], color)
	
	# draw reverse button
	elif button_type == "reverse":
		html += create_circle(size_y / 2, size_x - (size_y / 2) + 5, size_y / 2 + 5, shadow_color)
		html += create_polygon([(0 + 5, size_y + 5), (size_x / 4 + 5, 0 + 5), (size_x - (size_y / 2) + 5, 0 + 5), (size_x - (size_y / 2) + 5, size_y + 5)], shadow_color)	

		html += create_circle(size_y / 2, size_x - (size_y / 2), size_y / 2, outline_color)
		html += create_polygon([(0, size_y), (size_x / 4, 0), (size_x - (size_y / 2), 0), (size_x - (size_y / 2), size_y)], outline_color)	

		html += create_circle(size_y / 2 - 5, size_x - (size_y / 2), size_y / 2, color)
		html += create_polygon([(12, size_y - 5), (size_x / 4 + 2, 5), (size_x - (size_y / 2) - 5, 5), (size_x - (size_y / 2) - 5, size_y - 5)], color)		

	# draw middle type button
	elif button_type == "middle":
		html += create_polygon([(0 + 5, size_y + 5), (size_x / 4 + 5, 0 + 5), (size_x + 5, 0 + 5), (size_x * 3.0 / 4 + 5, size_y + 5)], shadow_color)
		html += create_polygon([(0, size_y), (size_x / 4, 0), (size_x, 0), (size_x * 3.0 / 4, size_y)], outline_color)
		html += create_polygon([(0 + 12, size_y - 5), (size_x / 4 + 2, 0 + 5), (size_x - 12, 0 + 5), (size_x * 3.0 / 4 - 2, size_y - 5)], color)

	# draw large buttons with special values
	elif button_type == "full":
		html += create_circle(size_y / 2, size_y / 2 + 5, size_y / 2 + 5, shadow_color)
		html += create_polygon([(size_y/2.0 + 5, 0 + 5),(size_y/2.0 + 5,size_y + 5),(size_x - size_y + 5, size_y + 5),(size_x + 5, 0 + 5)], shadow_color)
		html += create_circle(size_y / 2, size_y / 2, size_y / 2, outline_color)
		html += create_polygon([(size_y/2.0,0),(size_y/2.0,size_y),(size_x - size_y, size_y),(size_x, 0)], outline_color)
		html += create_circle(size_y / 2 - 5, size_y / 2, size_y / 2, color)
		html += create_polygon([(size_y/2.0,5),(size_y/2.0,size_y-5),(size_x - size_y - 2, size_y-5),(size_x - 12, 5)], color)

	# add words on the front
	if word:
		if button_type == "standard":
			html += create_smash_svg_text(word, (size_y / 2) - 7, size_y - 10 - offset_up, size_y, size_x* 3.0 / 4 - 20, background_color)
		elif button_type == "reverse":
			html += create_smash_svg_text(word, size_x / 4 - 7, size_y - 10 - offset_up, size_y, size_x* 3.0 / 4 - 20, background_color)
		elif button_type == "middle":
			html += create_smash_svg_text(word, size_x / 4 - 18, size_y - 10 - offset_up, size_y, size_x* 3.0 / 4 - 20, background_color)
		elif button_type == "full":
			html += create_smash_svg_text(word, (size_y / 2) - 7, size_y - 10 - offset_up, size_y, size_x - size_y - 20, background_color)
	
	# add the button ability
	if onclick:
		html += "</g>"

	html += "</svg>"
	return html

def generate_navbar(active=None, logged_in=False):
	style_dict = {
		'position': 'relative',
		'top': 0,
		'left': 0,
		'margin-top': '10px',
		'margin-bottom': '10px',
		'margin-right': 'auto',
		'margin-left': 'auto',
		'min-width':'1000px',
		'max-width': '1000px',
		'height': '55px',

	}

	# define the highlighting for the buttons
	smash_highlighted = active == "home" or active == "splash"
	login_highlighted = active == "login"
	logout_highlighted = active == "logout"
	register_highlighted = active == "register"
	profile_highlighted = active == "profile"
	unranked_highlighted = active == "unranked"
	ranked_highlighted = active == "ranked"

	# add the navbar div
	html = '<div '
	html += add_style(style_dict)
	html += '>'

	# add the main button
	html += create_smash_button(195, 50, 'rgb(255, 50, 10)', word = 'Smash', float_val='left', onclick='/', highlighted=smash_highlighted)
	
	# add the login specific buttons
	if not logged_in:
		html += create_smash_button(195, 50, 'rgb(10, 150, 50)', word = 'Register', float_val='right', button_type="reverse", onclick='/register', highlighted=register_highlighted)
		html += create_smash_button(195, 50, 'rgb(10, 50, 250)', word = 'Login', float_val='right', onclick='/login', highlighted=login_highlighted)
	else:
		html += create_smash_button(195, 50, '#666688', word = 'Logout', float_val='right', button_type="reverse", onclick='/logout', highlighted=logout_highlighted)
		html += create_smash_button(195, 50, '#93D620', word = 'Ranked', float_val='right', button_type="middle", onclick='/ranked', highlighted=ranked_highlighted)
		html += create_smash_button(195, 50, '#169FFA', word = 'Unranked', float_val='right', button_type="middle", onclick='/unranked', highlighted=unranked_highlighted)
		html += create_smash_button(195, 50, '#F2A705', word = 'Profile', float_val='right', button_type="middle", onclick='/profile', highlighted=profile_highlighted)
	html += '</div>'
	return html

def generate_main_div(inner):

	style_dict = {
		'top': 0,
		'left': 0,
		'position': 'relative',
		'margin-top': '10px',
		'margin-bottom': '10px',
		'margin-left': 'auto',
		'margin-right': 'auto',
		'min-width':'1000px',
		'max-width': '1000px',
	}

	html = '<div id="main_div"'
	html += add_style(style_dict)
	html += '>'

	style_dict = {
		'font-family': 'Helvetica, Arial',
		'font-weight':'500',
		'font-size':'32px',
		'top': 0,
		'left': 0,
		'position': 'relative',
		'margin-bottom': '10px',
		'margin-left': '10px',
		'margin-right': '10px',
	}	
	html += '<div id="text_div"'
	html += add_style(style_dict)
	html += '>'

	html += inner
	html += "</div></div>"
	return html

class HTMLPage:
	header = ""
	body = ""
	
	def __init__(self, page_css=None):
		self.body = ""
		self.header = ""
		if not page_css:
			self.header += add_css('css/basic.css')
		else:
			self.header += add_css(page_css)
		self.header += add_title("Smashed")
		self.header += add_ttf_font('/font/edosz.ttf', 'Edo')

	def add_header(self, item):
		self.header += item

	def add_body(self, item):
		self.body += item

	def get_html(self):
		return create_html(self.header, self.body)
