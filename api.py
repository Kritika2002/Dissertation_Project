import os 
import psycopg2
from flask import Flask,jsonify,request
from postgres import insert_db

app = Flask(__name__)

hostname = 'localhost'
database = 'weather'
username = 'postgres'
pwd = 'pim123K*'
port_id = '5433'

def  get_database_connection():
    connection = psycopg2.connect(
                host = hostname,
                dbname = database,
                user = username,
                password = pwd,
                port = port_id)  
    return connection

def insert_scraped_data():
    directory = "./output"
    files = os.listdir(directory)

    for file_name in files:
        if file_name.endswith('.txt'):
            file_path = os.path.join(directory,file_name)
            insert_db(file_path)

@app.route('/cities')
def index():
    # city_id = request.args.get('city_id')
    connection = get_database_connection()
    cur = connection.cursor()
    cur.execute('SELECT * FROM cities;')
    cities = cur.fetchall()
    cur.close()
    connection.close()
    return jsonify(cities)

# @app.route('/weather/<city_id>', methods=['GET'])
# def index1(city_id):
#     connection = get_database_connection()
#     cur = connection.cursor()
#     cur.execute('''SELECT *
#         FROM cities
#         INNER JOIN tomorrow_forecast ON cities.id = tomorrow_forecast.city_id
#         INNER JOIN tonight_forecast ON cities.id = tonight_forecast.city_id
#         WHERE cities.id = %s;
#         ''', (city_id))

#     weather = cur.fetchall()

#     cur.close()
#     connection.close()
#     return jsonify(weather)

# @app.route('/weather/forecast/today/<city_id>', methods=['GET'])
# def index2(city_id):
#     print('hello')
#     connection = get_database_connection()
#     cur = connection.cursor()
#     cur.execute('''SELECT *
#         FROM cities
#         INNER JOIN current_weather ON cities.id = current_weather.city_id
#         WHERE cities.id = %s;
#         ''', (city_id))

#     weather = cur.fetchall()

#     cur.close()
#     connection.close()
#     return jsonify(weather)

# @app.route('/weather/forecast/tonight/<city_id>', methods=['GET'])
# def index3(city_id):
#     print('hello')
#     connection = get_database_connection()
#     cur = connection.cursor()
#     cur.execute('''SELECT *
#         FROM cities
#         INNER JOIN tonight_forecast ON cities.id = tonight_forecast.city_id
#         WHERE cities.id = %s;
#         ''', (city_id))

#     weather = cur.fetchall()

#     cur.close()
#     connection.close()
#     return jsonify(weather)

# @app.route('/weather/forecast/tomorrow/<city_id>', methods=['GET'])
# def index5(city_id):
#     connection = get_database_connection()
#     cur = connection.cursor()
#     cur.execute('''SELECT *
#         FROM cities
#         INNER JOIN tomorrow_forecast ON cities.id = tomorrow_forecast.city_id
#         WHERE cities.id = %s;
#         ''', (city_id))

#     weather = cur.fetchall()

#     cur.close()
#     connection.close()
#     return jsonify(weather)

# @app.route('/weather/history/<city_id>', methods=['GET'])
# def index4(city_id):
#     print('hello')
#     connection = get_database_connection()
#     cur = connection.cursor()
#     cur.execute('''SELECT *
#         FROM cities
#         INNER JOIN historical_weather ON cities.id = historical_weather.city_id
#         WHERE cities.id = %s;
#         ''', (city_id))

#     weather = cur.fetchall()

#     cur.close()
#     connection.close()
#     return jsonify(weather)

if __name__ == '__main__':
    app.run(debug=True)
