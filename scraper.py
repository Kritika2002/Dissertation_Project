from bs4 import BeautifulSoup
import requests
from datetime import datetime
import os

# datetime object containing current date and time
now = datetime.now()
 
print("now =", now)

# dd/mm/YY H:M:S
dt_string = now.strftime("%d%m%Y-%H%M%S")
if os.name == 'nt':
    file_name = 'output/scrape_' + dt_string + '.txt'
else: 
    file_name = '/mnt/c/Users/LENOVO/Downloads/Dissertation_Project/output/scrape_' + dt_string + '.txt'

with open(file_name,'w') as f:

    #function to get station weather information 
    def station_weather():
            source = requests.get ('http://www.mfd.gov.np/weather/').text
            soup= BeautifulSoup(source,'lxml')

            weather = soup.find('table',class_='table')

            for station_row in weather.find_all('tr'):
                # print(station_row)
                column_values = station_row.find_all('td')
                for column in column_values:
                    f.write(column.text+'\n')

    city_ids = [22, 23, 24, 26, 27, 35, 28, 29, 31, 39, 38, 32, 33, 34, 1] # add more as needed

    #function to get weather data on the basis of city 
    def get_city_weather(city_id):
        city_source = requests.get('http://www.mfd.gov.np/city?id='+str(city_id)).text
        city_soup = BeautifulSoup(city_source,'lxml')

        weather = city_soup.find('div',class_='row')

        scraped_data = {
            'tonight': {
                'day': None,
                'temp': None,
                'rain_probability': None,
                'sun_info': None
            },
            'tomorrow': {
                'day': None,
                'temp': None,
                'rain_probability': None,
                'sun_info': None
            },
            'today': {
                'day': None,
                'temp': None,
                'rain_probability': None,
                'sun_info': None
            }
        }

        WEATHER_NOW_CLASSES = {'Weather Tonight': 'tonight', 'Weather Tomorrow': 'tomorrow', 'Weather Today':'today'}

        for weather_forecast in weather.find_all('div',class_='city-box city-forecast'):
            if (weather_forecast.find('h3').text not in WEATHER_NOW_CLASSES):
                print('Weather now div not in classes')
                continue
            
            weather_now = weather_forecast.find('div',class_='WeatherNow')
            div_array = [ div.text for div in weather_now.find_all('div', class_ = None) ]
            div_array.append(weather_forecast.find('div', class_='SunInfo').text)
            
            weather_key = WEATHER_NOW_CLASSES[weather_forecast.find('h3').text]
            scraped_data[weather_key] = dict(zip(scraped_data[weather_key].keys(), div_array))

            f.write(str(scraped_data))
            f.write('\n')

    station_weather()
    for city_id in city_ids:
        get_city_weather(city_id)
