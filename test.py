import requests
import json


# weather test
'''
WEATHER_API_KEY = '8f417a3430dd2d2d06d5bbb266b5d38f'
CURRENT_WEATHER_API = 'http://api.openweathermap.org/data/2.5/weather'
DAILY_WEATHER_API = 'http://api.openweathermap.org/data/2.5/forecast/daily'

def get_weather_json(city):

	# first api call to get city id
	current_weather = requests.get(CURRENT_WEATHER_API, params={'q': city, 'appid': WEATHER_API_KEY, 'units': 'metric'})

	if (current_weather and len(current_weather.json()) > 2):
		city_id = current_weather.json()['id']

		# second api call to get weather json
		current_weather = requests.get(DAILY_WEATHER_API, params={'id':city_id, 'appid': WEATHER_API_KEY, 'units': 'metric', 'cnt': '1'})
		print("Weather " + str(current_weather))

	return current_weather.json()

args = get_weather_json('portsaid')
print (args)
weather = "Today, " + args['list'][0]['weather'][0]['main'] + ' in ' + args['city']['name']
weather += " Maximum temprature is " + str(int(args['list'][0]['temp']['max'])) + " and Minimum temprature is "
weather += str(int(args['list'][0]['temp']['min']))
print(weather)
'''

# wiki test

WIKI_API = 'https://en.wikipedia.org/w/api.php'
def send_json_get_request(url, params):

	req = requests.get(url, params=params)

	if req.status_code != requests.codes.ok:
		#print("json get request faild" + req.text)
		pass
	else:
		#print("json get request success! " + req.text)
		pass

	return req.json()

def get_wiki_json(query):

	# search the api for query
	params = {'action': 'query', 'format': 'json', 'prop':'extracts', 'exintro': 'null', 'explaintext': 'null', 'titles': query}
	search_json = send_json_get_request(WIKI_API, params)

	page = search_json['query']['pages']
	pageid = list(page.keys())[0]

	# if nothing found
	if (pageid == '-1'):
		return json.dumps({'error': '404'})

	# we got a hit!
	else:
		# get title and summary
		title = page[str(pageid)]['title']
		summary = page[str(pageid)]['extract']
		# get thumbnail
		print(str(pageid))
		thumb_params = {'action': 'query', 'format': 'json', 'prop':'pageimages', 'piprop':'original', 'pageids': str(pageid)}
		thumb_json = send_json_get_request(WIKI_API, thumb_params)
		thumb_page = thumb_json['query']['pages'][str(pageid)]
		print(thumb_json)
		if 'thubmnail' in thumb_page:
			thumbnail = thumb_page['thumbnail']['original']
		else:
			thumbnail = 'https://cdn2.iconfinder.com/data/icons/stickerweather/256/na.png'

		article_url = 'https://en.wikipedia.org/?curid=' + str(pageid)

		wiki_json = {
			'id': str(pageid),
			'title': title,
			'thumbnail': thumbnail,
			'url': article_url,
			'summary': summary
		}
		# print(wiki_json)
		return wiki_json


my_json = get_wiki_json('stack overflow')

# print(my_json)