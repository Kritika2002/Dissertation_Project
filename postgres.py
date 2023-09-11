import os 
import psycopg2

hostname = 'localhost'
database = 'weather'
username = 'postgres'
pwd = 'pim123K*'
port_id = '5433'

def db_connection():
    try:
        connection = psycopg2.connect(
                host = hostname,
                dbname = database,
                user = username,
                password = pwd,
                port = port_id)
        return connection        
    except psycopg2.Error as error:
        print(error)

file_path ="./output"
        
def insert_db(file_path):
    try:
        connection = db_connection()
        cur = connection.cursor()

        with open(file_path,'r') as r:
            lines = r.readlines()
            for line in lines:
                insert_value ='''INSERT INTO tomorrow_forecast (id,
                                timestamp,
                                city_id,
                                expected_temperature,
                                expected_rainfall) VALUES (%s, %s, %s, %s, %s)'''
                cur.exectue(insert_value)    

        connection.commit()
        cur.close()
        connection.close()
    except Exception as error:
        print(error)
        

