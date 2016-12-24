import requests

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