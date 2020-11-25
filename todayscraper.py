import requests
from datetime import datetime, date, timedelta, time
import json

checkups = []
tables = []

stations = []
with open('stations.txt', mode="r", encoding="utf-8") as f:
    stations = f.read().splitlines()

for i in range(12):
    checkups.append(datetime(2019, 6, 4))
    tables.append([])

def getFirst(station_id):
    table = loadTable(station_id)
    if station_id == 0:
        return table[0][0], -1
    if station_id == len(stations) - 1:
        return -1, table[1][0]
    return table[0][0], table[1][0]

def getLast(station_id):
    table = loadTable(station_id)
    if station_id == 0:
        return table[0][-1], -1
    if station_id == len(stations) - 1:
        return -1, table[1][-1]
    return table[0][-1], table[1][-1]

def getNearest(station_id):
    now = datetime.now()
    tab = loadTable(station_id)
    
    scheduleForw = tab[0]
    scheduleBack = tab[1]

    back, forw, bi, fi = -1,-1,-1,-1

    for i, val in enumerate(scheduleForw):
        if val > now:
            forw = val
            fi = i
            break
    
    for i, val in enumerate(scheduleBack):
        if val > now:
            back = val
            bi = i
            break
    
    return forw, back, fi, bi

def getNext(station_id, fi, bi):
    tab = loadTable(station_id)
    
    scheduleForw = tab[0]
    scheduleBack = tab[1]

    fi += 1
    bi += 1

    if fi == len(scheduleForw) or fi == 0:
        fi = -1
        forw = -1
    else:
        forw = scheduleForw[fi]

    if bi == len(scheduleBack) or bi == 0:
        bi = -1
        back = -1
    else:
        back = scheduleBack[bi]

    return forw, back, fi, bi

def getSeveral(station_id, count):
    forwList = []
    backList = []
    forw, back, fi, bi = getNearest(station_id)

    if forw != -1:
        forwList.append(forw)
    if back != -1:
        backList.append(back)
    
    for i in range(count - 1):
        forw, back, fi, bi = getNext(station_id, fi, bi)
        if forw != -1:
            forwList.append(forw)
        if back != -1:
            backList.append(back)
    
    return forwList, backList

def loadTable(station_id):
    now = datetime.now()
    if (now - checkups[station_id]).total_seconds() < 3600:
        return tables[station_id]
    
    r = requests.get('http://209.182.216.197:5134/data/today')
    json_data = r.json()
    
    stations = json_data['stations']
    server_station_id = stations[station_id]['id']

    scheduleForw = json_data['schedule'][server_station_id][0]['schedule']
    scheduleBack = json_data['schedule'][server_station_id][1]['schedule']

    table = [[], []]

    for forw in scheduleForw:
        table[0].append(valToTime(forw))
    for back in scheduleBack:
        table[1].append(valToTime(back))
    
    table[0] = sorted(table[0])
    table[1] = sorted(table[1])

    tables[station_id] = table
    checkups[station_id] = now

    return table


def valToTime(val):
    tod = date.today()
    tom = tod + timedelta(days = 1)

    s = val.split(':')
    if len(s) != 3:
        return -1

    if int(s[0]) == 0 or int(s[0]) == 24:
        return datetime.combine(tom, time(0, int(s[1]), int(s[2])))
    else:
        return datetime.combine(tod, time(int(s[0]), int(s[1]), int(s[2])))
