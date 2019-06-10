import requests
from lxml import html
from datetime import date, datetime, timedelta, time

holidays = [
    date(2019, 7, 6),
    date(2019, 7, 8),
    date(2019, 8, 30),
    date(2019, 12, 2),
    date(2019, 12, 16),
    date(2019, 12, 17)
]

stations = []
with open('stations.txt', mode="r", encoding="utf-8") as f:
    stations = f.read().splitlines() 

def getStations():
    return stations

def isHoliday(d = (datetime.now() - timedelta(hours = 2)).date()):
    if d in holidays:
        return True
    if d.weekday() >= 5:
        return True
    return False

def valToTime(val):
    tod = date.today()
    day = timedelta(days=1)

    s = val.text_content().split(':')
    if len(s) != 3:
        return -1
    if s[0] != '24':
        return datetime.combine(tod, time(int(s[0]), int(s[1]), int(s[2])))
    return datetime.combine(tod + day, time(0, int(s[1]), int(s[2])))

checkups = []
tables = []
for i in range(12):
    checkups.append(datetime(2019, 6, 4))
    tables.append([])

def loadTable(station_id):
    if (datetime.now() - checkups[station_id]).total_seconds() < 600:
        return tables[station_id]
    h = ''
    if isHoliday():
        h = '/holiday'
    r = requests.get('http://metroalmaty.kz/?q=ru/schedule-list-view/' + str(station_id + 1) + h)
    tree = html.fromstring(r.content)
    checkups[station_id] = datetime.now()
    tab = tree.xpath('/html/body/div[2]/div[6]/div[2]/div[2]/div/div/div/table/tbody/tr')
    newtab = []
    if station_id == 0:
        for row in tab:
            newtab.append([valToTime(row)])
    elif station_id == 8:
        for row in tab:
            newtab.append([valToTime(row)])
    else:
        for row in tab:
            newtab.append([valToTime(row[0]), valToTime(row[1])])
    tables[station_id] = newtab
    return newtab

def getFirst(station_id):
    tab = loadTable(station_id)
    if station_id == 0:
        return -1, tab[0][0]
    if station_id == 8:
        return tab[0][0], -1
    return tab[0]

def getLast(station_id):
    tab = loadTable(station_id)
    if station_id == 0:
        return -1, tab[-1][0]
    if station_id == 8:
        return tab[-1][0], -1
    i = -2
    while tab[-1][0] == -1:
        tab[-1][0] = tab[i][0]
        i -= 1
    while tab[-1][1] == -1:
        tab[-1][1] = tab[i][1]
        i -= 1
    return tab[-1]

def getNearest(station_id):
    now = datetime.now()
    tab = loadTable(station_id)
    back, forw, bi, fi = -1,-1,-1,-1
    if station_id == 0:
        for val in tab:
            if val[0] == -1 or val[0] > now:
                back = val[0]
                bi = tab.index(val)
                return forw, back, fi, bi
    
    if station_id == 8:
        for val in tab:
            if val[0] == -1 or val[0] > now:
                forw = val[0]
                fi = tab.index(val)
                return forw, back, fi, bi

    for val in tab:
        if val[0] != -1 and val[0] > now and back == -1:
            back = val[0]
            bi = tab.index(val)
        if val[1] != -1 and val[1] > now and forw == -1:
            forw = val[1]
            fi = tab.index(val)

    return forw, back, fi, bi

def getNext(station_id, fi, bi):
    tab = loadTable(station_id)
    back, forw = -1,-1

    if station_id == 0:
        forw, fi = -1, -1
        if bi == -1 or bi >= len(tab) - 1:
            back = -1
            bi = -1
        else:
            bi += 1
            back = tab[bi][0]
        return forw, back, fi, bi
    
    if station_id == 8:
        back, bi = -1,-1
        if fi == -1 or fi >= len(tab) - 1:
            forw = -1
            fi = -1
        else:
            fi += 1
            forw = tab[fi][0]
        return forw, back, fi, bi

    if fi == -1 or fi >= len(tab) - 1:
        forw = -1
        fi = -1
    else:
        fi += 1
        forw = tab[fi][1]
    if bi == -1 or bi >= len(tab) - 1:
        back = -1
        bi = -1
    else:
        bi += 1
        back = tab[bi][0]
    return forw, back, fi, bi

def getSeveral(station_id, count):
    forw, back = [], []
    f, b, fi, bi = getNearest(station_id)
    if f != -1:
        forw.append(f)
    if b != -1:
        back.append(b)
    
    for i in range(count - 1):
        f, b, fi, bi = getNext(station_id, fi, bi)
        if f != -1:
            forw.append(f)
        if b != -1:
            back.append(b)
    
    return forw, back