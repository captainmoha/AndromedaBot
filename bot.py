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
MSG_API = 'https://graph.facebook.com/v2.6/me/messages'

@app.route('/', methods=['GET'])
def verify():

	if (request.args.get('hub.verify_token', '') == 'IF_HOPE_IS_THE_ENGINE_OF_THE_SOUL_THEN'):

		print ('Verification successful!')
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
		send_text_message(PAT, sender, message)

	return 'ok'


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


def send_text_message(token, recipient, text):
	"""
		Send the message text to recipient with id recipient.
	"""

	# send post request to the api with the message


	params = {'access_token': token}
	print ("id: " + str(recipient))
	data = json.dumps({
		'recipient': {'id': recipient},
		'message': {'text': get_reply(text)}
		})

	headers = {'Content-type': 'application/json'}

	req = requests.post(MSG_API, params=params, data=data, headers=headers)

	if req.status_code != requests.codes.ok:
		print ("failed to send message: " + req.text)

def get_reply(text):
	'''
		get suitable reply for the user's text message
	'''
	raw_txt = text
	text = escape_query(text).lower()
	reply = None
	rows = None

	cursor.execute("SELECT line_id, text FROM LineSearch WHERE text Match ? AND text LIKE ?", ('^'+text+'*', '%'+text+'%'))
	rows = cursor.fetchall()

	# nothing in the database then see if it's an emoji message
	if (rows == None or len(rows) == 0):
		emoji_msg = extract_emoji(raw_txt)

		# if it's not an emoji message try the database again less strictly
		if (len(emoji_msg) == 0):
			cursor.execute("SELECT line_id, text FROM LineSearch WHERE text Match ? AND text LIKE ?", ('^'+text.split(' ')[0]+'*', '%'+text.split(' ')[0]+'%'))
			rows = cursor.fetchall()

			if (rows == None or len(rows) == 0):
				return apologize()
			else:
				return smart_reply(rows, bad=True)

		else:
			return emoji_msg

	else:
		return smart_reply(rows)

		

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
	return "Let's talk about something else..."
# get_reply('what do you do for fun')

if __name__ == '__main__':
	# for c9
	# app.run(debug=True, host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))
	
	# heroku
	app.run()
			
