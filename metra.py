import requests
import json
from collections import OrderedDict
import datetime

def parse_datetime(odd_time):
    unixtime = int(odd_time.strip('/Date()')) / 1000
    return datetime.datetime.fromtimestamp(unixtime)

def get_stations_from_line(line_id):
    result = requests.get('http://metrarail.com/content/metra/en/home/jcr:content/trainTracker.get_stations_from_line.json', params={'trackerNumber': 0, 'trainLineId': line_id})
    stations = result.json(object_pairs_hook=OrderedDict)['stations']

    return [{'id': station['id'], 'name': station['name']} for station in stations.values()]

def get_arrival_times(line_id, origin_station_id, destination_station_id):
    headers = {
        'Content-Type': 'application/json; charset=UTF-8'
    }
    payload = {
        "stationRequest": {
            "Corridor": line_id,
            "Destination": destination_station_id,
            "Origin": origin_station_id
        }
    }
    result = requests.post('http://12.205.200.243/AJAXTrainTracker.svc/GetAcquityTrainData', headers=headers, data=json.dumps(payload))

    d = result.json()['d']
    data = json.loads(d)

    def build_arrival(train):
        return {'estimated_dpt_time': parse_datetime(train['estimated_dpt_time']),
             'scheduled_dpt_time': parse_datetime(train['scheduled_dpt_time']),
             'dpt_station': train['dpt_station'],
             'train_num': train['train_num'],
             'state': train['RunState']}

    arrivals = []
    for (k,v) in data.iteritems():
        if k.startswith('train'):
            arrivals.append(build_arrival(v))

    return arrivals

if __name__ == '__main__':
    stations = get_stations_from_line('UP-N')
    for station in stations:
        print "%(id)s: %(name)s" % station

    times = get_arrival_times('UP-N', 'MAINST', 'OTC')
    for arrival in times:
        print "Train %(train_num)s is leaving %(dpt_station)s at %(estimated_dpt_time)s." % arrival