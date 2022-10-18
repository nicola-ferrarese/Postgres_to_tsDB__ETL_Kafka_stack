from datetime import datetime

import requests
import psycopg2

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(dbname="postgres",
                                user="postgres",
                                password="postgres",
                                host="localhost",
                                port="5433")
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        exit()
    #finally:
    #    if conn is not None:
    #        conn.close()
    #        print('Database connection closed.')

#r=requests.get("http://www.example.com/", headers={"Content-Type":"text"})

def add_all_values(auth_token):
    """insert all measure inside db"""
    try:
        conn = connect()
        conn.autocommit = True
        ## Get all values from API:
        ## values is a dictionary of dictionaries
        values = requests.get("https://cloud.wi4b.com/api/rs485-environment-sensor-measure-by-device/2/?page=1&size=20000&startInterval=2022-8-1T22:00:01.000&endInterval=2022-10-10T21:59:59.490",
                              headers={"Connection":"keep-alive",
                                       "Authorization": auth_token},
                              verify=False).json()

        for i in range(len(values)):
            cursor = conn.cursor()
            # Preparing SQL queries to INSERT a record into the database.
            try:
                timestamp = datetime.strptime(values[i]['measureTimestamp'], "%Y-%m-%dT%H:%M:%SZ")
            except(Exception) as wrong_format:
                print("---> Trying different format:")
                timestamp = datetime.strptime(values[i]['measureTimestamp'], "%Y-%m-%dT%H:%M:%S.%fZ")

            query = f"INSERT INTO env_measure(device_id,timestamp,air_temp,id,air_pres,air_hum) " \
                    f"VALUES ('{values[i]['rs485environmentSensor']}'," \
                    f"'{timestamp}'," \
                    f"'{values[i]['airTemperature']}'," \
                    f"'{values[i]['id']}'," \
                    f"'{values[i]['airPressure']}'," \
                    f"'{values[i]['airHumidity']}') "
            cursor.execute(query)
            print(f"Inserted record taken at: {timestamp}")
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    #
    # add_all_values("Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo4NiwidXNlcm5hbWUiOiJmLm5pY29sYTk4QGdtYWlsLmNvbSIsImV4cCI6MTY2NjEwMDIxOSwiZW1haWwiOiJmLm5pY29sYTk4QGdtYWlsLmNvbSIsIm9yaWdfaWF0IjoxNjY1OTU5MjYwfQ.iZCMJeJ0rMIb3_06FAANFcTlXzO_fMjCGg1Vwzy71OI")


