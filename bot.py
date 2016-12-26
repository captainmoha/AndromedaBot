from flask import Flask, request
import json
import requests
import string
import sqlite3
import random
import os
import csv
import re

app = Flask(__name__)

# database
DB = 'movies.db'
db_con = sqlite3.connect(DB, check_same_thread=False)
cursor = db_con.cursor()

# read emoji
with open('emoji.csv', 'r') as fCSV:
	reader = csv.reader(fCSV)
	emoji = next(reader)
	print (str(len(emoji)) + ' ' + str(type(emoji))) 

# read smilys
with open('smiley.csv', 'r') as fCSV:
	reader = csv.reader(fCSV)
	smileys = {}

	for row in reader:
		smileys[row[0]] = row[1]

	print (str(len(smileys)) + ' ' + str(type(smileys))) 

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
PAT = 'EAAXVXB27pBsBAF1uLpTMmtJd2pUEJFe2FWlFccjG5ZCJ1TzFXIu7YCeqtqoZAdiECkZBRzDb34dzzFDwMGSez0M2BpiMO4hL633ZBo5sHsHYHDNt4R9SOydGlwTeZC2wjgGkFPZCz5YqCY9Nf27BIZCTyt3KZAPfYTpbMgZAgBbbRrQZDZD'
WEATHER_API_KEY = '8f417a3430dd2d2d06d5bbb266b5d38f'
CURRENT_WEATHER_API = 'http://api.openweathermap.org/data/2.5/weather'
DAILY_WEATHER_API = 'http://api.openweathermap.org/data/2.5/forecast/daily'
MSG_API = 'https://graph.facebook.com/v2.6/me/messages'
PERSIST_MENU_API = 'https://graph.facebook.com/v2.6/me/thread_settings'
# for article summary
WIKI_API = 'https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=&explaintext=&titles=Stack%20Overflow&format=json'
# # url
# 'https://en.wikipedia.org/?curid=21721040'
# # thumbnail
# 'https://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&pageids=21721040'
IMDB_API = 'http://www.omdbapi.com'

@app.route('/', methods=['GET'])
def verify():

	if (request.args.get('hub.verify_token', '') == 'IF_HOPE_IS_THE_ENGINE_OF_THE_SOUL_THEN'):

		print ('Verification successful!')
		add_persist_menu()
		return request.args.get('hub.challenge', '')

	else:
		print ('Verification faild!')
		return 'Error, wrong token'



@app.route('/', methods=['POST'])
def handle_messages():

	print ('handling messages')

	payload = request.get_json()

	print (payload)

	for sender, message in messaging_events(payload):
		print ('Incoming from %s: %s' % (sender, message))

		# handle different types of messages. text or attachments
		send_text_message(sender, message)

	return 'ok'


def add_persist_menu():
	'''
		adds a persistant menu to chat in order to help users or share the bot
		https://developers.facebook.com/docs/messenger-platform/thread-settings/persistent-menu
	'''
	menu = json.dumps({
			"setting_type" : "call_to_actions",
			"thread_state" : "existing_thread",
			"call_to_actions":[
			  {
			    "type":"postback",
			    "title":"Need help?",
			    "payload":"DEVELOPER_DEFINED_PAYLOAD_FOR_HELP"
			  },
			  {
			    "type":"postback",
			    "title":"Share me?",
			    "payload":"DEVELOPER_DEFINED_PAYLOAD_FOR_START_ORDER"
			  }
			]
		})

	params = {'access_token': PAT}
	headers = {'Content-type': 'application/json'}
	
	req = requests.post(PERSIST_MENU_API, params=params, data=menu, headers=headers)
	
	if req.status_code != requests.codes.ok:
		print("failed to add persistant menu " + req.text)
	else:
		print("added persistent menu " + req.text)


def remove_persist_menu():

	delete_menu = json.dumps({
				"setting_type":"call_to_actions",
				"thread_state":"existing_thread"
				})

	params = {'access_token': PAT}
	headers = {'Content-type': 'application/json'}
	
	req = requests.delete(PERSIST_MENU_API, params=params, data=delete_menu, headers=headers)
	
	if req.status_code != requests.codes.ok:
		print ("failed to delete persistant menu " + req.text)

def messaging_events(payload):
	'''
	Generate tuples of (sender_id, message_text) from the provided payload.
 	'''

	# data = json.loads(payload)
	events = payload['entry'][0]['messaging']

	for event in events:
		if 'message' in event:

			# handle different types of content
			if 'text' in event['message']:
				yield event['sender']['id'], event['message']['text']

			# cases other than text

			# else if 'attachments' in event['message']:
			#	yield event['sender']['id'], event['message']['attachments']
				
			else:
				yield event['sender']['id'], 'u wot m8?'


def send_text_message(recipient, text):
	"""
		Send the message text to recipient with id recipient.
	"""

	# see if the user is commanding and handle user commands

	commandList = text.split(' ')
	if (commandList[0].lower() in ['andromeda', 'rommie', 'rom', 'bot', 'lassie']):
		handle_commands(recipient, commandList)

	# if it's a normal message
	else:
		# send post request to the api with the message
		send_post(recipient, get_reply(text))


def get_reply(text):
	'''
		get suitable reply for the user's text message
	'''
	# the user sent an image (not supported yet)
	if (text == 'u wot m8?'):
		return 'u wot m8?'


	raw_txt = text
	emoji_msg = extract_emoji(raw_txt)
	text = escape_query(text).lower()
	reply = None
	rows = None

	cursor.execute("SELECT line_id, text FROM LineSearch WHERE text Match ? AND text LIKE ?", ('^'+text+'*', '%'+text+'%'))
	rows = cursor.fetchall()

	# nothing in the database then see if it's an emoji message
	if (rows == None or len(rows) == 0):
		

		# if it's not an emoji message try the database again less strictly
		if (len(emoji_msg) == 0):
			cursor.execute("SELECT line_id, text FROM LineSearch WHERE text Match ? AND text LIKE ?", ('^'+text.split(' ')[0]+'*', '%'+text.split(' ')[0]+'%'))
			rows = cursor.fetchall()

			if (rows == None or len(rows) == 0):
				return apologize() + emoji_msg
			else:
				return smart_reply(rows, bad=True) + emoji_msg

		else:
			return emoji_msg

	else:
		return smart_reply(rows) + emoji_msg

		

def smart_reply(rows, bad=False):
	'''
		get supposedly smart reply from database and return it
	'''

	print("Rows: " + str(len(rows)))
	randomIndex = random.randrange(0, len(rows))
	row = rows[randomIndex]

	print("id: %s - text: %s" % (row[0], row[1]))
	reply_id = int(row[0]) + 1
	print("reply id: " + str(reply_id))

	cursor.execute('SELECT text FROM LineSearch WHERE line_id = ?', (reply_id,))
	reply = cursor.fetchone()
	if (reply == None):
		# if we don't find an answer just reply with what we have!
		return rows[randomIndex][1]

	if (not bad):
		print("reply: %s" % reply[0])
	else:
		print("bad reply: %s" % reply[0])
	

	return reply[0]

def extract_emoji(txt):
	'''
		extract emojis and smileys from a message contact them
	'''
	msg = ""
	
	for emo in txt:
		if emo in emoji:
			msg += emo

	tokens = txt.split(' ')
	print(tokens)
	# print(smileys.keys())
	for smiley in tokens:
		if smiley in smileys.keys():
			msg += smileys[smiley]

	return msg

def escape_query(s):
	'''
		remove all but alphanumeric charcters and white space
	'''
	return re.sub(r'[^\s\w]', '', s)

def apologize():
	'''
		When we've got nothin to say
	'''
	return "Let's talk about something else..."


def handle_commands(recipient, commandList):
	'''
		Handle user commands
	'''

	supported_commands = ['movie', 'weather']

	print("Gonna handle commands baby!")

	if (len(commandList) < 3) or (commandList[1] not in supported_commands):
		send_post(recipient, "Invalid command my friend!")

	# movie
	elif (commandList[1] == 'movie'):
		movie_title = " ".join(commandList[2:])

		# len of response is 2 when the movie is not found
		response = get_movie_json(movie_title)

		
		if (response and len(response) > 2):
			# we found a movie!
			send_post(recipient, "", text_only=False, args=response)
		else:
			send_post(recipient, "Invalid movie or series name. Please, try again honey.")
			send_post(recipient, "", text_only=False, args={'img_url': 'http://i.imgur.com/DhgMkzW.jpg'})

	# weather
	elif (commandList[1] == 'weather'):
		city = " ".join(commandList[2:4])
		weather_json = get_weather_json(city)

		if (weather_json and len(weather_json) > 2):
			# we found the city!
			send_post(recipient, text_only=False, args=weather_json)
		else:
			send_post(recipient, "Invalid city name. Please, try again sweetie.")
			send_post(recipient, text_only=False, args={'img_url': 'http://i.imgur.com/DhgMkzW.jpg'})

	
def send_post(recipient, text="", text_only=True, args={}):
	# send post request to the api with the message

	params = {'access_token': PAT}
	print ("id: " + str(recipient))

	# handle text
	if text_only:
		data = json.dumps({
			'recipient': {'id': recipient},
			'message': {'text': text}
			})

	# handle movies
	elif 'Title' in args:
		data = json.dumps({
		'recipient': {'id': recipient},
		'message':{
			'attachment':{
				'type':"template",
				'payload':{
					'template_type':"generic",
					'elements':[
						{
							'title': args['Title'] + ' (' + args['Year'] + ')\nRating: ' + args['imdbRating'],
							'subtitle': args['Plot'],
							'image_url': args['Poster'] if not (args['Poster'] == 'N/A') else 'https://cdn2.iconfinder.com/data/icons/stickerweather/256/na.png',
							'buttons':[
								{
									'type':"web_url",
									'url':"http://www.imdb.com/title/" + args['imdbID'] if not (args['imdbID'] == 'N/A') else 'http://www.imdb.com',
									'title':"View on imdb"
								},
								{
									'type':"element_share"
								}
							],
			
						}
					]
				}
			}
		}
		})
	

	# handle weather
	elif 'city' in args:

		weather = "Today, " + args['list'][0]['weather'][0]['main'] + ' in ' + args['city']['name'] + ', ' + args['city']['country']
		weather += "\nMax : " + str(int(args['list'][0]['temp']['max'])) + " Min: "
		weather += str(int(args['list'][0]['temp']['min']))

		data = json.dumps({
			'recipient': {'id':recipient},
			'message': {'text': weather}
			})

	# handle image
	elif 'img_url' in args:
		data = json.dumps({
			'recipient': {'id': recipient},
			'message': {
				'attachment': {
					'type': 'image',
					'payload': {
						'url': args['img_url']
					}
				}
			}
			})
	
	headers = {'Content-type': 'application/json'}
	
	req = requests.post(MSG_API, params=params, data=data, headers=headers)
	
	if req.status_code != requests.codes.ok:
		print ("failed to send message: " + req.text)


def get_movie_json(movie_title):
	'''
		Make get request to the oIMDB API to get movie info and return it as json
	'''

	movie = requests.get(IMDB_API, params={'t': movie_title})

	return movie.json()

def get_weather_json(city):
	'''
		Get weather data from openweathermap.org and return it as json
	'''

	# first api call to get city id
	current_weather = requests.get(CURRENT_WEATHER_API, params={'q': city, 'appid': WEATHER_API_KEY, 'units': 'metric'})

	if (current_weather and len(current_weather.json()) > 2):
		city_id = current_weather.json()['id']

		# second api call to get weather json
		current_weather = requests.get(DAILY_WEATHER_API, params={'id':city_id, 'appid': WEATHER_API_KEY, 'units': 'metric', 'cnt': '1'})
		print("Weather " + str(current_weather))

	return current_weather.json()
	


# get_reply('what do you do for fun')

if __name__ == '__main__':
	# for c9
	# app.run(debug=True, host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))
	
	# heroku
	app.run()

			
