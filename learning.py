from google.transit import gtfs_realtime_pb2
from urllib.request import Request, urlopen
import os
import time

# trips_feed = gtfs_realtime_pb2.FeedMessage()
# req = Request('https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-ace')
# req.add_header('x-api-key', os.environ['MTA_API_KEY'])
# response = urlopen(req)
# trips_feed.ParseFromString(response.read())
# print(trips_feed.entity[0])



'''
The response is an array which looks something like this:
trip_update {
  trip {
    trip_id: "048200_A..N"
    start_time: "08:02:00"
    start_date: "20220630"
    route_id: "A"
  }
  stop_time_update {
    arrival {
      time: 1656596786
    }
    departure {
      time: 1656596786
    }
    stop_id: "A05N"
  }
  stop_time_update {
    arrival {
      time: 1656596853
    }
    departure {
      time: 1656596853
    }
    stop_id: "A03N"
  }
}

I need to find a resource with information for each stop.
'''
print('\n\n')

feed = gtfs_realtime_pb2.FeedMessage()
req = Request('https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts')
req.add_header('x-api-key', os.environ['MTA_API_KEY'])
response = urlopen(req)
feed.ParseFromString(response.read())
current_time = int(time.time())
# print(feed.entity[0])
for entity in feed.entity:
  print(entity.alert.header_text.translation[0].text)