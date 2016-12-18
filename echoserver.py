from flask import Flask, request
import json
import requests
import string
import sqlite3
import random
import os

app = Flask(__name__)

# database
DB = 'movies.db'
db_con = sqlite3.connect(DB, check_same_thread=False)
cursor = db_con.cursor()


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
		'message': {'text': get_reply(text).decode('unicode_escape')}
		})

	headers = {'Content-type': 'application/json'}

	req = requests.post(MSG_API, params=params, data=data, headers=headers)

	if req.status_code != requests.codes.ok:
		print ("failed to send message: " + req.text)

def get_reply(text):
	text = text.lower()
	reply = None
	cursor.execute("SELECT line_id, text FROM LineSearch WHERE text Match ? AND text LIKE ?", ('^'+text+'$', '%'+text+'%'))
	rows = cursor.fetchall()
	for row in rows:
		print("id: %s - text: %s" % (row[0], row[1]))
		reply_id = int(row[0]) + 1
		print("reply id: " + str(reply_id))
		cursor.execute('SELECT text FROM LineSearch WHERE line_id = ?', (reply_id,))
		reply = cursor.fetchone()
		break
	print(str(len(rows)))

	

	
	if (reply == None):
		return "Let's talk about something else..."

	print("reply: %s" % reply[0])

	return reply[0]


get_reply('what do you do for fun')

if __name__ == '__main__':
	# for c9
	# app.run(debug=True, host=os.getenv('IP', '0.0.0.0'),port=int(os.getenv('PORT', 8080)))
	
	# heroku
	app.run()
			
