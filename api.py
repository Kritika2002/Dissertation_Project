#api for the system

#import libraries
import os 
import psycopg2
from flask import Flask,jsonify,request
from postgres import insert_db
from werkzeug.exceptions import HTTPException
from datetime import datetime

app = Flask(__name__)

hostname = 'localhost'
database = 'weather'
username = 'postgres'
pwd = 'pim123K*'
port_id = '5433'

def get_database_connection():
    connection = psycopg2.connect(
                host = hostname,
                dbname = database,
                user = username,
                password = pwd,
                port = port_id)  
    return connection


def fetch_exec(*fnargs, all=False):
    connection = get_database_connection()
    cur = connection.cursor()
    cur.execute(*fnargs)
    print('all: ', all)
    if (all):
        ret = cur.fetchall()
    else:
        ret = cur.fetchone()
    cur.close()
    connection.close()
    return ret 

#routes for current weather and city name
@app.route('/cities')
def cities():
    ret_cities = fetch_exec('SELECT name FROM cities;', all=True)
    return jsonify([city[0] for city in ret_cities])

@app.route('/weather/current', methods = ['GET'])
@app.route('/weather/current/', methods = ['GET'])
@app.route('/weather/current/<city_name>', methods = ['GET'])
def current_weather(city_name=None):
    ret_weather = fetch_exec(f'''
        SELECT DISTINCT ON (cities.name) cities.name, ts, max_temperature, min_temperature, rain_probability
        FROM observed_weather
        INNER JOIN cities ON cities.id = observed_weather.city_id
        { f"WHERE cities.name = '{city_name}'" if city_name else ''}
        ORDER BY cities.name, ts DESC;
    ''', all=(True if city_name is None else False))

    print(ret_weather)

    if (ret_weather is None):
        return 'City name did not match', 404, {'Content-Type': 'text/plain; charset=utf-8'}

    keys = ['name', 'timestamp', 'max_temperature', 'min_temperature', 'rain_probability']
    if (city_name is not None):
        ret_weather = dict(zip(keys, ret_weather))
    else:
        ret_weather = [dict(zip(keys, values)) for values in ret_weather]

    return jsonify(ret_weather), 200, {'Content-Type': 'text/plain; charset=utf-8'}

#routes for historic weather and city name
@app.route('/weather/historic/', methods = ['GET'])
@app.route('/weather/historic/<from_iso>/<till_iso>/', methods = ['GET'])
@app.route('/weather/historic/<from_iso>/<till_iso>/<city_name>', methods = ['GET'])
def historic_weather(from_iso = None, till_iso = None, city_name = None):
    print('start: ', from_iso, 'stop', till_iso)
    parsed_from_till = [None, None]
    try:
        parsed_from_till = [datetime.strptime(iso, '%Y-%m-%d-%H-%M-%S') for iso in [from_iso, till_iso]]
        print(parsed_from_till)
    except Exception as e:
        print(e)
        return 'Please specify from and till in YYYY-MM-DD-HH-MM-SS format, for url /weather/historic/[from]/[till]', 404
    
    ret_weather = fetch_exec(f'''
        SELECT cities.name, ts, max_temperature, min_temperature, rain_probability
        FROM observed_weather
        INNER JOIN cities ON cities.id = observed_weather.city_id
        WHERE ts > '{parsed_from_till[0].isoformat()}' AND ts < '{parsed_from_till[1].isoformat()}'
        { f"AND cities.name = '{city_name}'" if city_name else ''}
        ORDER BY cities.name, ts DESC;
    ''', all=True)
    print(ret_weather)

    if (ret_weather is None):
        return 'City name did not match or no data', 404, {'Content-Type': 'text/plain; charset=utf-8'}

    keys = ['name', 'timestamp', 'max_temperature', 'min_temperature', 'rain_probability']
    if (city_name is not None):
        ret_weather = dict(zip(keys, ret_weather))
    else:
        ret_weather = [dict(zip(keys, values)) for values in ret_weather]

    return jsonify(ret_weather), 200, {'Content-Type': 'text/plain; charset=utf-8'}

#routes for current forecast and city name
@app.route('/forecast/current', methods = ['GET'])
@app.route('/forecast/current/', methods = ['GET'])
@app.route('/forecast/current/<city_name>', methods = ['GET'])
def current_forecast(city_name=None):
    ret_weather = fetch_exec(f'''
        SELECT DISTINCT ON (cities.name) cities.name, for_day, expected_temperature_low, expected_temperature_high, rain_probability
        FROM forecast
        INNER JOIN cities ON cities.id = forecast.city_id
        { f"WHERE cities.name = '{city_name}'" if city_name else ''}
        ORDER BY cities.name, for_day DESC;
    ''', all=(True if city_name is None else False))
    print(ret_weather)

    if (ret_weather is None):
        return 'City name did not match', 404, {'Content-Type': 'text/plain; charset=utf-8'}

    keys = ['name', 'for_day', 'expected_temperature_low', 'expected_temperature_high', 'rain_probability']
    if (city_name is not None):
        ret_weather = dict(zip(keys, ret_weather))
    else:
        ret_weather = [dict(zip(keys, values)) for values in ret_weather]

    return jsonify(ret_weather), 200, {'Content-Type': 'text/plain; charset=utf-8'}

#routes for current forecast and city name
@app.route('/forecast/historic/', methods = ['GET'])
@app.route('/forecast/historic/<for_day_iso>', methods = ['GET'])
@app.route('/forecast/historic/<for_day_iso>/', methods = ['GET'])
@app.route('/forecast/historic/<for_day_iso>/<city_name>', methods = ['GET'])
def historic_forecast(for_day_iso=None, city_name=None):
    print('for_day_iso: ', for_day_iso)
    parsed_day = None
    try:
        parsed_day = datetime.strptime(for_day_iso, '%Y-%m-%d')
        print(parsed_day)
    except Exception as e:
        print(e)
        return 'Please specify day in ISO format!', 400, {'Content-Type': 'text/plain; charset=utf-8'}
    finally:
        print('parsed day is: ', parsed_day)

    
    ret_weather = fetch_exec(f'''
        SELECT DISTINCT ON (cities.name) cities.name, for_day, expected_temperature_low, expected_temperature_high, rain_probability
        FROM forecast
        INNER JOIN cities ON cities.id = forecast.city_id
        WHERE for_day = '{parsed_day.date().isoformat()}'
        { f"AND cities.name = '{city_name}'" if city_name else ''}
        ORDER BY cities.name, for_day DESC;
    ''', all=(True if city_name is None else False))
    print(ret_weather)

    keys = ['name', 'for_day', 'expected_temperature_low', 'expected_temperature_high', 'rain_probability']
    if (city_name is not None):
        ret_weather = dict(zip(keys, ret_weather))
    else:
        ret_weather = [dict(zip(keys, values)) for values in ret_weather]
    
    return jsonify(ret_weather), 200

#routes for current sun_info and city name
@app.route('/sun_info/current', methods = ['GET'])
@app.route('/sun_info/current/', methods = ['GET'])
@app.route('/sun_info/current/<city_name>', methods = ['GET'])
def current_sun_info(city_name=None):
    ret_weather = fetch_exec(f'''
        SELECT DISTINCT ON (cities.name) cities.name, for_day, to_json(sunrise), to_json(sunset)
        FROM sun_info
        INNER JOIN cities ON cities.id = sun_info.city_id
        { f"WHERE cities.name = '{city_name}'" if city_name else ''}
        ORDER BY cities.name, for_day DESC;
    ''', all=(True if city_name is None else False))
    print(ret_weather)

    if (ret_weather is None):
        return 'City name did not match', 404, {'Content-Type': 'text/plain; charset=utf-8'}

    keys = ['name', 'for_day', 'sunrise', 'sunset']
    if (city_name is not None):
        ret_weather = dict(zip(keys, ret_weather))
    else:
        ret_weather = [dict(zip(keys, values)) for values in ret_weather]

    return jsonify(ret_weather), 200, {'Content-Type': 'text/plain; charset=utf-8'}


#routes for historic sun info and city name
@app.route('/sun_info/historic/', methods = ['GET'])
@app.route('/sun_info/historic/<for_day_iso>', methods = ['GET'])
@app.route('/sun_info/historic/<for_day_iso>/', methods = ['GET'])
@app.route('/sun_info/historic/<for_day_iso>/<city_name>', methods = ['GET'])
def historic_sun_info(for_day_iso=None, city_name=None):
    print('for_day_iso: ', for_day_iso)
    parsed_day = None
    try:
        parsed_day = datetime.strptime(for_day_iso, '%Y-%m-%d')
        print(parsed_day)
    except Exception as e:
        print(e)
        return 'Please specify day in ISO format!', 400, {'Content-Type': 'text/plain; charset=utf-8'}
    finally:
        print('parsed day is: ', parsed_day)

    
    ret_weather = fetch_exec(f'''
        SELECT DISTINCT ON (cities.name) cities.name, for_day, to_json(sunrise), to_json(sunset)
        FROM sun_info
        INNER JOIN cities ON cities.id = sun_info.city_id
        WHERE for_day = '{parsed_day.date().isoformat()}'
        { f"AND cities.name = '{city_name}'" if city_name else ''}
        ORDER BY cities.name, for_day DESC;
    ''', all=(True if city_name is None else False))
    print(ret_weather)

    keys = ['name', 'for_day', 'sunrise', 'sunset']
    if (city_name is not None):
        ret_weather = dict(zip(keys, ret_weather))
    else:
        ret_weather = [dict(zip(keys, values)) for values in ret_weather]
    return jsonify(ret_weather), 200


if __name__ == '_main_':
    app.run(debug=True)