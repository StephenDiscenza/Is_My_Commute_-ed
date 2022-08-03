import requests
import csv
import sqlite3
from sqlite3 import Error
from werkzeug.security import generate_password_hash


def create_cxn_on_db(db_name):
    try:
        cxn = sqlite3.connect(db_name)
    except Error as e:
        raise Exception(f'Failed to connect to or create {db_name} db with error: {e}')
    return cxn


def setup_db():
    cxn = create_cxn_on_db('commute_check.db')
    cursor = cxn.cursor()
    # Create the stations table which stores static information about subway stations
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS stations 
                    (station_id int NOT NULL,
                    complex_id int NOT NULL,
                    lines text NOT NULL,
                    gtfs_stop_id varchar(255) NOT NULL,
                    stop_name varchar(255) NOT NULL,
                    latitude real NOT NULL,
                    longitude real NOT NULL)
                    ''')
    cursor.execute('''
                    CREATE INDEX IF NOT EXISTS station_names_index
                    ON stations(stop_name)
                    ''')
    # Create the users table
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    username TEXT NOT NULL UNIQUE,
                    hash TEXT NOT NULL)
                    ''')
    cursor.execute('''
                    CREATE INDEX IF NOT EXISTS username_index
                    ON users(username)
                    ''')
    # Create the commutes table
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS commutes
                    (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users (id))
                    ''')
    cursor.execute('''
                    CREATE INDEX IF NOT EXISTS commutes_user_id_index
                    ON commutes(user_id)
                    ''')
    # Create the commute_legs table
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS commute_legs
                    (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    commute_id INTEGER NOT NULL,
                    origin_name TEXT NOT NULL,
                    origin_id varchar(255) NOT NULL,
                    termination_name TEXT NOT NULL,
                    termination_id varchar(255) NOT NULL,
                    line varchar(255) NOT NULL,
                    FOREIGN KEY (commute_id) REFERENCES commutes (id))
                    ''')
    cursor.execute('''
                    CREATE INDEX IF NOT EXISTS commute_id_index
                    ON commute_legs(commute_id)
                    ''')
    
    cxn = update_station_ids(cxn)
    cxn.commit()
    cxn.close()
    return


def generic_lookup(query:str, data:list):
    cxn = create_cxn_on_db('commute_check.db')
    cxn.row_factory = sqlite3.Row
    cursor = cxn.cursor()
    result = cursor.execute(query, data).fetchall()
    cxn.close()
    return result


def update_station_ids(cxn):
    response = requests.get('https://atisdata.s3.amazonaws.com/Station/Stations.csv')
    cursor = cxn.cursor()
    cursor.execute('DELETE FROM stations')
    reader = csv.DictReader(response.content.decode().split('\n'), delimiter=',')
    for row in reader:
        cursor.execute('''INSERT INTO stations (station_id, complex_id, lines, gtfs_stop_id, stop_name, latitude, longitude)
                          VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                          [row['Station ID'], row['Complex ID'], row['Daytime Routes'], row['GTFS Stop ID'], row['Stop Name'], row['GTFS Latitude'], row['GTFS Longitude']])
    return cxn


def get_user_info(username):
    return generic_lookup( "SELECT * FROM users WHERE username = ?", [username])


def add_user(request):
    '''Insert new user into the db with a hashed password'''
    cxn = create_cxn_on_db('commute_check.db')
    cursor = cxn.cursor()
    cursor.execute("INSERT INTO users (username, hash) values(?, ?)", [request.form.get(
        "username"), generate_password_hash(request.form.get("password"))])
    cxn.commit()
    cxn.close()


def get_commutes(user_id):
    '''Retrieves all commutes belonging to the supplied user id'''
    return generic_lookup("SELECT * FROM commutes WHERE user_id = ?", [user_id])


def get_leg_data(commute_id):
    '''Get's origin and destination data for each leg of a commute'''
    return generic_lookup("SELECT * FROM commute_legs WHERE commute_id = ?", [commute_id])


def add_commute_to_db(commute_data):
    '''Adds the data from the supplied payload to the db'''
    cxn = create_cxn_on_db('commute_check.db')
    cursor = cxn.cursor()
    ''' 
    Expecting to get a json body with the format:
    {
        "name": "commute name",
        "user_id": "id",
        "legs": [
            {
                "line": "N",
                "originName": "Astoria, Ditmars Blvd.",
                "originId": "A01",
                "terminationName": "59th Street, Lexington Ave.",
                "terminationId": "A10"
            }
        ]
    }
    '''
    commute_id = cursor.execute("INSERT INTO commutes (name, user_id) values(?, ?) RETURNING id", [commute_data['name'], commute_data['user_id']]).fetchall()[0][0]
    for leg in commute_data['legs']:
        cursor.execute("INSERT INTO commute_legs (commute_id, origin_name, origin_id, termination_name, termination_id, line) values(?, ?, ?, ?, ?, ?)", [commute_id, leg['originName'], leg['originId'], leg['terminationName'], leg['terminationId'], leg['line']])

    cxn.commit()
    cxn.close()


def delete_commute_from_db(commute_id):
    '''Deletes a commute record and associated commute legs from the db'''
    cxn = create_cxn_on_db('commute_check.db')
    cursor = cxn.cursor()
    cursor.execute("DELETE FROM commute_legs WHERE commute_id = ?", [commute_id])
    cursor.execute("DELETE FROM commutes WHERE id = ?", [commute_id])
    cxn.commit()
    cxn.close()


def get_stations_by_line(line:str):
    '''Fetch data for all stations on the provided line'''
    return generic_lookup("SELECT stop_name, gtfs_stop_id FROM stations WHERE lines LIKE ?", [f'%{line}%'])