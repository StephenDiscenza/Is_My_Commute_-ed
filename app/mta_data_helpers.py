from google.transit import gtfs_realtime_pb2
from urllib.request import Request, urlopen
from .database_helpers import get_leg_data
import os
import time

def get_commute_alets(commute_id) -> bool:
    '''Check for all alerts related to the lines the provided commute uses'''
    commute_legs = get_leg_data(commute_id)
    lines = [commute_leg['line'] for commute_leg in commute_legs]
    alerts = []

    feed = gtfs_realtime_pb2.FeedMessage()
    req = Request('https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/camsys%2Fsubway-alerts')
    req.add_header('x-api-key', os.environ['MTA_API_KEY'])
    response = urlopen(req)
    feed.ParseFromString(response.read())
    current_time = int(time.time())
    
    def check_temporal_relevance(active_periods, current_time) -> bool:
        # Not all elements have the same fields so trys are used
        for active_period in active_periods:
            try:
                # Check that there is a start time and that it is before the current time.
                if current_time >= active_period.start:
                    try:
                        # Check that there is an end time and that it's after the current time
                        if current_time <= active_period.end:
                            return True
                    except AttributeError:
                        # Assume alert is ongoing if there isn't an end time
                        return True
            except AttributeError:
                continue
        return False
            
    for entity in feed.entity:
        # Check that the alert is for a line we care about
        # Check that the alert is applicable at this moment in time
        for informed_entity in entity.alert.informed_entity:
            try:
                if informed_entity.route_id in lines and check_temporal_relevance(entity.alert.active_period, current_time):
                    for text_version in entity.alert.header_text.translation:
                        if text_version.language == 'en':
                            alerts.append(text_version.text)
            except AttributeError:
                continue
    return alerts


def analyze_commute_alerts(alerts: list) -> bool:
    '''
    Given a list of alert data, determine if the commute is bad
    '''
    keyword_severities = {
        'delay': 2,
        'local': 2,
        'NYPD': 2,
        'runs via': 1,
        'stops': 1
    }
    # A score >= means the commute is bad
    score = 0
    for alert in alerts:
        # There is a base line score of 1 for any alert  
        score += 1
        for keyword in keyword_severities.keys():
            if keyword in alert:
                score += keyword_severities[keyword]
                break
    if score >= 3:
        return True
    return False
