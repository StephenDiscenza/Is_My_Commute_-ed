import requests
import csv
import sqlite3
from sqlite3 import Error


def create_cxn_on_db(db_name):
    try:
        cxn = sqlite3.connect(db_name)
    except Error as e:
        raise Exception(f'Failed to connect to or create {db_name} db with error: {e}')
    return cxn


def setup_db():
    cxn = create_cxn_on_db('static_data.db')
    cursor = cxn.cursor()
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stations 
                    (station_id int NOT NULL,
                    complex_id int NOT NULL,
                    gtfs_stop_id varchar(255) NOT NULL,
                    stop_name varchar(255) NOT NULL,
                    latitude real NOT NULL,
                    longitude real NOT NULL)
                    ''')
    cursor.execute('''
                    CREATE INDEX IF NOT EXISTS station_names_index
                    ON stations(stop_name)
                    ''')
    cxn = update_station_ids(cxn)
    cxn.commit()
    cxn.close()
    return


def update_station_ids(cxn):
    response = requests.get('https://atisdata.s3.amazonaws.com/Station/Stations.csv')
    cursor = cxn.cursor()
    cursor.execute('DELETE FROM stations')
    reader = csv.DictReader(response.content.decode().split('\n'), delimiter=',')
    for row in reader:
        cursor.execute('''INSERT INTO stations (station_id, complex_id, gtfs_stop_id, stop_name, latitude, longitude)
                          VALUES (?, ?, ?, ?, ?, ?)''', [row['Station ID'], row['Complex ID'], row['GTFS Stop ID'], row['Stop Name'], row['GTFS Latitude'], row['GTFS Longitude']])
    return cxn


if __name__ == '__main__':
    setup_db()