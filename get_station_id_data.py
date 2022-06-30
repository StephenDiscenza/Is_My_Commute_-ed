import requests


def update_station_ids():
    response = requests.get('https://atisdata.s3.amazonaws.com/Station/Stations.csv')
    with open('station_id_data.csv', 'wb') as f:
        f.write(response.content)



if __name__ == '__main__':
    update_station_ids()