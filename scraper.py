#scraper for the system

#import libraries
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import os
import psycopg2
import re

hostname = 'localhost'
database = 'weather'
username = 'postgres'
pwd = 'pim123K*'
port_id = '5433'

#connection to the database
connection = psycopg2.connect(
    host = hostname,
    dbname = database,
    user = username,
    password = pwd,
    port = port_id
)

cur = connection.cursor()


# datetime object containing current date and time
print('Database connection is successful!')
now = datetime.now()
 
print("now =", now)

def insert_station_weather(cursor, columns):
    # print('columns:: ', columns)
    city_weathers = [columns[i:i+4] for i in range(0, len(columns), 4)]
    print('city_weathers:: ', city_weathers)
    for city_weather in city_weathers:
        try:
            print(city_weather)

            if (len(city_weather) == 4):
                cursor.execute('SELECT id FROM cities WHERE name = %s', [city_weather[0].lower()])
                city_id = cursor.fetchone()
                print(city_id)
                try:
                    expected_rainfall = float(city_weather[3].replace('*', ''))
                except ValueError:
                    expected_rainfall = 0.

                print('Inserting to db values: ', [ float(city_weather[1]), float(city_weather[2]), expected_rainfall, now.isoformat()])
                cursor.execute('INSERT INTO observed_weather (city_id, max_temperature,  min_temperature, rain_probability, ts) VALUES (%s, %s, %s, %s, %s);',
                            [city_id[0], float(city_weather[1]), float(city_weather[2]), expected_rainfall, now.isoformat()])
        except Exception as e:
            print('Error while inserting station weather: ', e)

def insert_city_weather(cursor, scraped_data, city_id):
    print('city_id: ', city_id)
    print('scraped_data: ', scraped_data)
    
    for key in scraped_data:
        print()
        if (scraped_data[key]['day'] is not None):
            # extracting day
            day_regex = r'\((.+?)\)'
            month_day = re.search(day_regex, scraped_data[key]['day']).group()
            dt_text = f"{now.year} {month_day[1:-1]}"
            day = datetime.strptime(dt_text, '%Y %b %d')

            # extracting temp values
            temp_regex = r'\d+'
            vals = re.findall(temp_regex, scraped_data[key]['temp'])
            if len(vals) != 2:
                break

            # extracting rain probability
            rain_regex = r'((\d+))\s*?%'
            rain_probability = re.search(rain_regex, scraped_data[key]['rain_probability'])

            params = [ 
                day.date().isoformat(),
                city_id,
                int(vals[0]),
                int(vals[1]),
                rain_probability.group(1) if rain_probability else None,
                0 if key == 'today' else 1 if key == 'tonight' else 2
            ]

            print('Inserting to db values: ', params)
            cursor.execute('''
                INSERT INTO forecast (for_day, city_id, expected_temperature_low, expected_temperature_high, rain_probability, weather_class)
                VALUES (%s, %s, %s, %s, %s, %s);
            ''', params)


            if (scraped_data[key]['sun_info'] is not None and len(scraped_data[key]['sun_info']) > 28):
                # also inserting sun_info values here
                sun_info_regex = r'(\d+:\d+\s+[AaPp][Mm])'
                sunrise_set = re.findall(sun_info_regex, scraped_data[key]['sun_info'])
                if (len(sunrise_set) != 2):
                    break
                
                sunrise_set = [datetime.strptime(x, '%I:%M %p').replace(year=now.year, month=now.month, day=day.day).time().isoformat(timespec='minutes') for x in sunrise_set]
                print('Inserting sun info: ', sunrise_set)
                cursor.execute('''
                    INSERT INTO sun_info (for_day, city_id, sunrise, sunset)
                    VALUES (%s, %s, %s, %s)
                               ''', 
                  [day.date().isoformat(), city_id, *sunrise_set]
                )

            connection.commit()



# dd/mm/YY H:M:S
dt_string = now.strftime("%d%m%Y-%H%M%S")
if os.name == 'nt':
    file_name = 'output/scrape_' + dt_string + '.txt'
else: 
    file_name = './output/scrape_' + dt_string + '.txt'

#function to get station weather information 
def station_weather():
    source = requests.get ('http://www.mfd.gov.np/weather/').text
    soup= BeautifulSoup(source,'lxml')

    weather = soup.find('table',class_='table')

    columns = []

    for station_row in weather.find_all('tr'):
        # print(station_row)
        column_values = station_row.find_all('td')
        for column in column_values:
            # f.write(column.text+'\n')
            columns.append(column.text)

    return columns

city_ids = [21,22, 23, 24, 25,26, 27,28,29,30,31,32,33,34, 35, 36,37,39, 38,1] # add more as needed

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

        # f.write(str(scraped_data))
        # f.write('\n')

    return scraped_data

insert_station_weather(cur, station_weather())
for city_id in city_ids:
    try:
        insert_city_weather(cur, get_city_weather(city_id), city_id)
    except Exception as e:
        print('Failed trying to insert city weather for id', city_id, '\nreason:', e)

def fetch_city_weather(city_id, datetime):
    cur.execute("")
    return city_id
        
connection.commit()
connection.close()