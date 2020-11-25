import traceback, sys
import vk, random, re, json
import todayscraper, secret
import requests

token = secret.LONGPOLL_TOKEN
session = vk.Session(access_token=token)
api = vk.API(session, v = '5.126')

lps = api.groups.getLongPollServer(group_id = 183308654)
key = lps['key']
server = lps['server']
ts = lps['ts']

patterns = [re.compile('райымбек', re.I), re.compile('жибек|жібек', re.I),
    re.compile('алмал', re.I), re.compile('аба', re.I), re.compile('байкон|байқон', re.I),
    re.compile('театр|ауэз', re.I), re.compile('алатау', re.I), re.compile('сайран', re.I),
    re.compile('москва|мәскеу', re.I)]

def findStation(s):
    for i in range(len(patterns)):
        if re.match(patterns[i],s):
            return i
    return -1

stations = todayscraper.stations
actions = [{'type':'text','label':s} for s in stations]
buttons = [{'action':a,'color':'secondary'} for a in actions]
buttons = [buttons[0:3],buttons[3:6],buttons[6:]]
keyboard = {'buttons':buttons,'one_time':False}
keyboard = json.dumps(keyboard,ensure_ascii=False)

exception_counter = 0

while True:
    try :
        r = requests.get(server + '?act=a_check&key={0}&ts={1}&wait=25'.format(key, ts))
        json = r.json()

        if 'failed' in json:
            error_code = json['failed']
            if error_code != 1:
                lps = api.groups.getLongPollServer(group_id = 183308654)
                key = lps['key']
                server = lps['server']
                ts = lps['ts']
                continue

        ts = json['ts']
        updates = json['updates']

        for update in updates:
            if update['type'] == 'message_new':
                message = update['object']['message']
                peer_id = message['peer_id']

                if not api.groups.isMember(group_id='almetro', user_id=peer_id):
                    api.messages.send(peer_id = peer_id, message='Подпишитесь чтобы пользоваться ботом', random_id = random.randint(10000,999999))
                    continue

                text = message['text']
                station_id = findStation(text)
                
                if (station_id == -1):
                    api.messages.send(peer_id = peer_id, message = "Станция не найдена", keyboard = keyboard, random_id = random.randint(10000,999999))
                    continue
                
                forw, back = todayscraper.getSeveral(station_id, 3)
                reply = 'Расписание для станции ' + stations[station_id] + ':\r\n'

                if len(forw) == 0 and len(back) == 0:
                    reply += 'К сожалению, сейчас поездов нет'

                if len(forw) != 0:
                    reply += '⬅️ Москва:\r\n'
                    for fw in forw:
                        reply += fw.strftime("%H:%M:%S") + '\r\n'

                if len(back) != 0:
                    reply += '➡️ Райымбек батыра:\r\n'
                    for bc in back:
                        reply += bc.strftime("%H:%M:%S") + '\r\n'

                api.messages.send(peer_id = peer_id, message = reply, keyboard = keyboard, random_id = random.randint(10000,999999))
                exception_counter = 0
    
    except Exception as e:
        traceback.print_exc()
        exception_counter += 1
        if exception_counter > 5:
            api.messages.send(peer_id = 317356180, message = 'FATAL ERROR: 5 EXCEPTIONS IN A ROW', keyboard = keyboard, random_id = random.randint(10000,999999))
            sys.exit()
    