from datetime import datetime
import requests
import psycopg2
import sys
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
                                port="5600")
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        exit()

def add_all_values(auth_token):
    """insert all measure inside db"""
    try:

        conn = connect()
        conn.autocommit = True
        cursor = conn.cursor()
        try:
            query = 'DROP SCHEMA inventory CASCADE;'
            cursor.execute(query)
        except(Exception ):
            print('Inventory table not present, skipping')
        query = 'CREATE TABLE IF NOT EXISTS public.env_measure ('\
                    'id int4 NOT NULL, '\
                    'device_id int4 NULL, '\
                    '"timestamp" timestamp NULL, '\
                    'air_temp float4 NULL, '\
                    'air_pres float4 NULL, '\
                    'air_hum float4 NULL, '\
                    'CONSTRAINT env_measure_pk PRIMARY KEY (id));'
        cursor.execute(query)
        try:
            ## Get all values from API:
            ## values is a dictionary of dictionaries
            values = requests.get("https://cloud.wi4b.com/api/rs485-environment-sensor-measure-by-device/2/?page=1&size=20000&startInterval=2022-8-1T22:00:01.000&endInterval=2022-10-10T21:59:59.490",
                                  headers={"Connection":"keep-alive",
                                           "Authorization": auth_token},
                                  verify=False).json()

            for i in range(len(values)):

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
                        f"'{values[i]['airHumidity']}') ON CONFLICT DO NOTHING "
                cursor.execute(query)
                print(f"Inserted record taken at: {timestamp}")
        except(Exception, psycopg2.DatabaseError) as error:
            print("Could not Validate connection or Insert record in the database\n\n The tables are created though!")
        conn.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)

    # add_all_values("Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo4NiwidXNlcm5hbWUiOiJmLm5pY29sYTk4QGdtYWlsLmNvbSIsImV4cCI6MTY2NjEwMDIxOSwiZW1haWwiOiJmLm5pY29sYTk4QGdtYWlsLmNvbSIsIm9yaWdfaWF0IjoxNjY1OTU5MjYwfQ.iZCMJeJ0rMIb3_06FAANFcTlXzO_fMjCGg1Vwzy71OI")

if __name__ == "__main__":
    try:
        add_all_values(sys.argv[1])
    except:
        add_all_values("FOO")
        print('Auth token not specified!!')
