import os 
import psycopg2

hostname = 'localhost'
#database = 'weather'
username = 'postgres'
pwd = 'pim123K*'
port_id = '5433'

connection = None
cur = None

try:
        connection = psycopg2.connect(
                host = hostname,
                dbname = database,
                user = username,
                password = pwd,
                port = port_id)
        
        cur = connection.cursor()
        
        create_script = ('''CREATE TABLE IF NOT EXISTS cities (
                                id      SERIAL PRIMARY KEY,
                                name    varchar(255) NOT NULL
                                )
                        ''',
                        '''CREATE TABLE IF NOT EXISTS historical_weather (
                                id SERIAL PRIMARY KEY,
                                city_id INTEGER REFERENCES cities(id),
                                timestamp timestamp NOT NULL,
                                max_temperature DECIMAL(5, 2),
                                min_temperature DECIMAL(5, 2),
                                expected_rainfall DECIMAL(5, 2)
                                )
                        ''',
                        '''CREATE TABLE IF NOT EXISTS current_weather (
                                id SERIAL PRIMARY KEY,
                                city_id INTEGER REFERENCES cities(id),
                                temperature DECIMAL(5, 2),
                                expected_rainfall DECIMAL(5, 2)
                                )
                        ''',
                        '''CREATE TABLE IF NOT EXISTS tonight_forecast (
                                id SERIAL PRIMARY KEY,
                                timestamp timestamp NOT NULL,
                                city_id INTEGER REFERENCES cities(id),
                                expected_temperature DECIMAL(5, 2),
                                expected_rainfall DECIMAL(5, 2)
                                )
                        ''',
                        '''CREATE TABLE IF NOT EXISTS tomorrow_forecast (
                                id SERIAL PRIMARY KEY,
                                timestamp timestamp NOT NULL,
                                city_id INTEGER REFERENCES cities(id),
                                expected_temperature DECIMAL(5, 2),
                                expected_rainfall DECIMAL(5, 2)
                                )
                        '''
        )
        for create in create_script:
                cur.execute(create)

        insert_script = 'INSERT INTO cities (id, name) VALUES (%s, %s)'
        insert_values = [(1, 'Birgunj'), (2, 'Kathmandu'), (3, 'Pokhara')]

        insert_script1 = '''INSERT INTO current_weather (id,
                                city_id,
                                temperature,
                                expected_rainfall) VALUES (%s, %s, %s, %s)'''
        insert_values1 = [(1, 1,23,4), (2, 2, 34, 5), (3,3, 40, 5)]

        insert_script2 = '''INSERT INTO historical_weather (id,
                                city_id,
                                timestamp ,
                                max_temperature,
                                min_temperature,
                                expected_rainfall) VALUES (%s, %s, %s, %s, %s, %s)'''
        
        insert_values2 = [(1,1, '2016-06-22 19:10:25-07', 25, 20, 4), (2,2,'2016-06-22 19:10:25-07', 21, 25, 3), (3,3,'2016-06-22 19:10:25-07', 20, 18, 4)]

        insert_script3 = '''INSERT INTO tonight_forecast (id,
                                timestamp,
                                city_id,
                                expected_temperature,
                                expected_rainfall) VALUES (%s, %s, %s, %s, %s)'''
        
        insert_values3 = [(1,'2016-06-22 19:10:25-07', 1,23,0)]

        insert_script4 = '''INSERT INTO tomorrow_forecast (id,
                                timestamp,
                                city_id,
                                expected_temperature,
                                expected_rainfall) VALUES (%s, %s, %s, %s, %s)'''
        insert_values4 = [(1,'2016-06-22 19:10:25-07', 1,23,0)]

        for record in insert_values:
                cur.execute(insert_script, record)

        for record1 in insert_values1:
                cur.execute(insert_script1, record1)
        
        for record2 in insert_values2:
                cur.execute(insert_script2, record2)
        
        for record3 in insert_values3:
                cur.execute(insert_script3, record3)
        
        for record4 in insert_values4:
                cur.execute(insert_script4, record4)

        connection.commit()
        
except Exception as error:
        print(error)
finally:
        if cur is not None:
                cur.close()
        if connection is not None:
                 connection.close()