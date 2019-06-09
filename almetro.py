from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler, Filters
from telegram import InlineKeyboardButton, Message, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ParseMode
import timescraper, secret

updater = Updater(secret.TOKEN)

keys = {'Первый поезд':'F', 'Последний поезд':'L', 'Ближайший':'N'}

stations = []
with open('stations.txt', mode="r", encoding="utf-8") as f:
    stations = f.read().splitlines() 

def start(bot, update):
    keyboard = [['Первый поезд','Последний поезд'],['Ближайший']]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False, resize_keyboard=True)
    update.message.reply_text('🚇 Привет! Я бот для поиска поездов в алматинском метро! 🚇')
    update.message.reply_text('🚉 Выберите какой поезд вам нужен', reply_markup=markup)

def any_mes(bot, update):
    mt = update.message.text
    if not mt in keys:
        update.message.reply_text('Такой команды нет')
    keyboard = []
    for i in range(0,len(stations),2):
        keyboard.append([InlineKeyboardButton(
            stations[i], callback_data = keys[mt] + str(i))])
        if i + 1 < len(stations):
            keyboard[-1].append(InlineKeyboardButton(
                stations[i+1], callback_data = keys[mt] + str(i+1)))
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('🚉 Выберите станцию:', reply_markup=reply_markup)

def button(bot, update):
    keyboard = []
    data = update.callback_query.data
    rep = ''

    if data[0] == 'F':
        fw, bc = timescraper.getFirst(int(data[1:]))
    elif data[0] == 'L':
        fw, bc = timescraper.getLast(int(data[1:]))
        rep += 'Внимание! Последний поезд может быть не запущен!\r\n'
    elif data[0] == 'N':
        fw, bc, fi, bi = timescraper.getNearest(int(data[1:]))
        callback = 'X'+data[1:]+'*{0}*{1}'.format(fi,bi)
        keyboard = [[InlineKeyboardButton(
            'Следующий',callback_data=callback)]]
    elif data[0] == 'X':
        args = data[1:].split('*')
        args = list(map(int, args))
        fw, bc, fi, bi = timescraper.getNext(args[0],args[1],args[2])
        callback = 'X'+str(args[0])+'*{0}*{1}'.format(fi,bi)
        keyboard = [[InlineKeyboardButton(
            'Следующий',callback_data=callback)]]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if fw != -1:
        rep += '⬅️ *' + fw.strftime("%H:%M:%S") + '* - ' + stations[0] + '\r\n'
    if bc != -1:
        rep += '➡️ *' + bc.strftime("%H:%M:%S") + '* - ' + stations[-1]
    
    if rep == '':
        bot.send_message(text='Ничего не найдено', chat_id=update.callback_query.message.chat_id,
            parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    
    bot.send_message(text=rep, chat_id=update.callback_query.message.chat_id,
        parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler(Filters.all, any_mes))
updater.dispatcher.add_handler(CallbackQueryHandler(button))
updater.start_polling() 
updater.idle()