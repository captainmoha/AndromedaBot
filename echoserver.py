from flask import Flask, request
import json
import requests


app = Flask(__name__)

# This needs to be filled with the Page Access Token that will be provided
# by the Facebook App that will be created.
PAT = 'EAAXVXB27pBsBAF1uLpTMmtJd2pUEJFe2FWlFccjG5ZCJ1TzFXIu7YCeqtqoZAdiECkZBRzDb34dzzFDwMGSez0M2BpiMO4hL633ZBo5sHsHYHDNt4R9SOydGlwTeZC2wjgGkFPZCz5YqCY9Nf27BIZCTyt3KZAPfYTpbMgZAgBbbRrQZDZD'
MSG_API = 'https://graph.facebook.com/v2.6/me/messages'

@app.route('/', methods=['GET'])
def verify():

	if (request.args.get('hub.verify_token', '') == 'IF_HOPE_IS_THE_ENGINE_OF_THE_SOUL_THEN'):

		print 'Verification successful!'
		return request.args.get('hub.challenge', '')

	else:
		print 'Verification faild!'
		return 'Error, wrong token'


@app.route('/', methods=['POST'])
def handle_messages():

	print 'handling messages'

	payload = request.get_date()

	print payload

	for sender, message in messaging_events(payload):
		print 'Incoming from %s: %s' % (sender, message)
		send_message(PAT, sender, message)

	return 'ok'


def messaging_events(payload):
	'''
		Generate tuples of (sender_id, message_text) from the provided payload.
  	'''

  	data = json.loads(payload)
  	events = data['entry'][0]['messaging']

  	for event in events:
  		if 'message' in event:
  			message = event['message']

  			# handle different types of content
  			if 'text' in message:


def send_text_message(token, recipient, text):
	"""
		Send the message text to recipient with id recipient.
 	"""

 	# send post request to the api with the message

 	params = {'access_token': token}

 	data = json.dumps({
 		'recipient': {'id': recipient},
 		'message': {'text': text.decode('unicode_escape')}
 		})

 	headers = {'Content-type': 'application/json'}

 	req = requests.post(MSG_API, params, headers)

 	if req.status_code != requests.codes.ok:
 		print "failed to send message: " + req.text

if __name__ == '__main__':
	app.run(debug=True)
  			