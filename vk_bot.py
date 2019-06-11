from bottle import route, run, template, request
import vk, random, re, json
import timescraper, secret

token = secret.VK_TOKEN
session = vk.Session(access_token=token)
api = vk.API(session, v = '5.50')

with open('init_msg.txt', mode="r", encoding="utf-8") as f:
    init_msg = f.read()

stations = timescraper.stations
actions = [{'type':'text','label':s} for s in stations]
buttons = [{'action':a,'color':'secondary'} for a in actions]
buttons = [buttons[0:3],buttons[3:6],buttons[6:]]
keyboard = {'buttons':buttons,'one_time':False}
keyboard = json.dumps(keyboard,ensure_ascii=False)

patterns = [re.compile('райымбек', re.I), re.compile('жибек|жібек', re.I),
    re.compile('алмал', re.I), re.compile('аба', re.I), re.compile('байкон|байқон', re.I),
    re.compile('театр|ауэз', re.I), re.compile('алатау', re.I), re.compile('сайран', re.I),
    re.compile('москва|мәскеу', re.I)]


def findStation(s):
    for i in range(len(patterns)):
        if re.match(patterns[i],s):
            return i
    return -1

@route('/almetro',method='POST')
def index():
    data = request.json
    if not 'type' in data:
        return 'Type is not specified'
    datatype = data['type']
    if datatype == 'confirmation':
        return secret.VK_CONFIRM
    elif datatype == 'message_new':
        d = data['object']['body']
        user_id = data['object']['user_id']
        if not api.groups.isMember(group_id='almetro',user_id=user_id):
            api.messages.send(peer_id = user_id, message='Подпишитесь чтобы пользоваться ботом', random_id = random.randint(10000,999999))
            return 'ok'
        if len(d) == 1 and d in '123456789':            
            station_id = int(d) - 1
            forw, back = timescraper.getSeveral(station_id, 3)
            reply = 'Расписание для станции ' + stations[station_id] + ':\r\n'
            
            if len(forw) == 0 and len(back) == 0:
                reply += 'К сожалению, сейчас поездов нет'

            if len(forw) != 0:
                reply += '⬅️ Райымбек Батыра:\r\n'
                for fw in forw:
                    reply += fw.strftime("%H:%M:%S") + '\r\n'

            if len(back) != 0:
                reply += '➡️ Москва:\r\n'
                for bc in back:
                    reply += bc.strftime("%H:%M:%S") + '\r\n'
            
            api.messages.send(peer_id = user_id, message = reply, keyboard = keyboard, random_id = random.randint(10000,999999))
        
        else:
            station_id = findStation(d)

            if station_id == -1:
                api.messages.send(peer_id = user_id, message = init_msg, keyboard = keyboard, random_id = random.randint(10000,999999))
                return 'ok'
            
            forw, back = timescraper.getSeveral(station_id, 3)
            reply = 'Расписание для станции ' + stations[station_id] + ':\r\n'
            
            if len(forw) == 0 and len(back) == 0:
                reply += 'К сожалению, сейчас поездов нет'

            if len(forw) != 0:
                reply += '⬅️ Райымбек Батыра:\r\n'
                for fw in forw:
                    reply += fw.strftime("%H:%M:%S") + '\r\n'

            if len(back) != 0:
                reply += '➡️ Москва:\r\n'
                for bc in back:
                    reply += bc.strftime("%H:%M:%S") + '\r\n'
            
            api.messages.send(peer_id = user_id, message = reply, keyboard = keyboard, random_id = random.randint(10000,999999))
            
    return 'ok'

run(host='0.0.0.0', port=80)