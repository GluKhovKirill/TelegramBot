#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup #, Bot #, ReplyKeyboardRemove
from keys import get_key
from translator import YandexDictionary
from count import MathExecutor
from bash import get_quote
from weather import YandexWeather
 
 
logging.basicConfig(level=logging.INFO, filename="TelegramBot.log",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') #TODO: level=loging.INFO
 
 
class Translator:
    def translate_start(self, bot, update, user_data):
        user_data['job'] = user_data.get('job', [])
        if not user_data['job']:
            user_data['job'] = 1
            get_info(update)
            text = "Переход в режим переводчика!\nЕсли написать мне фразу на русском, я переведу "
            text += "её на английский и наоборот.\nДля выхода используйте /stop\n"
            text += '(Если Вам интересно, переведено с помощью сервисов «API «Яндекс.Словарь» и "Яндекс.Переводчик"\n'
            text += "http://api.yandex.ru/dictionary/ https://translate.yandex.ru)."
            update.message.reply_text(text, reply_markup=STOP_MARKUP)
            return 1
        else:
            logging.warning("ERR"+str(user_data['job']))
    
    def translate(self, bot, update, user_data):
        if user_data['job'] == 1:
            user = get_info(update, "TRANSLATOR_REQ")['user']
            answer = translator.analyze_and_translate(update.message.text)
            answer += '\n(Если Вам интересно, переведено с помощью сервисов «API «Яндекс.Словарь» и "Яндекс.Переводчик"\n'
            answer += "http://api.yandex.ru/dictionary/ https://translate.yandex.ru)."
            logging.info('TRANSLATOR_ANS TO '+user+': '+answer)
            update.message.reply_text(answer)
        else:
            logging.warning("ERR"+str(user_data['job']))        
            pass
   
    def translate_stop(self, bot, update, user_data):
        user_data['job'] = None
        get_info(update)
        update.message.reply_text("Выход из режима переводчика!", reply_markup=MARKUP)
        return ConversationHandler.END
    pass
 
 
class Counter:
    def count_start(self, bot, update, user_data):
        user_data['job'] = user_data.get('job', [])
        if not user_data['job']:
            user_data['job'] = 2
            get_info(update)
            text = "Переход в режим вычислителя!\nНапишите мне пример, и я его вычислю"
            text += "\n(Не больше 1 операнда за раз!)"
            update.message.reply_text(text, reply_markup=STOP_MARKUP)
            return 2
        else:
            logging.warning("ERR"+str(user_data['job']))        
   
    def count(self, bot, update, user_data):
        if user_data['job'] == 2:
            user = get_info(update, "COUNT_REQ")['user']
            msg = update.message.text.replace(" ", "")
            n = 0
            data = ["", "", ""]
            last_symbol = msg[0]
            for symbol in msg:
                if symbol.isdigit() != last_symbol.isdigit() and symbol != ".":
                    n += 1
                data[n] += symbol
                if symbol != ".":
                    last_symbol = symbol
            if 'pi' in data:
                data[0], data[2] = "", ""
                data[1] = 'pi'
            if 'e' in data:
                data[0], data[2] = "", ""
                data[1] = 'e'
            answer = MathExecutor(data[0], data[1], data[2]).execute()
            logging.info('COUNT_ANS TO '+user+': '+answer)
            update.message.reply_text(answer) 
        else:
            logging.warning("ERR"+str(user_data['job']))        
        pass
   
    def count_stop(self, bot, update, user_data):
        user_data['job'] = None
        get_info(update)
        update.message.reply_text("Выход из режима вычислителя!", reply_markup=MARKUP)
        return ConversationHandler.END    
    pass
 
 
class QuoteGrabber:
    def quotes_start(self, bot, update, user_data):
        user_data['job'] = user_data.get('job', [])
        if not user_data.get('job', []):
            user_data['job'] = 3
            #ReplyKeyboardMarkup([["/stop"]], one_time_keyboard=False)
            user_data['quote_ids'] = user_data.get('quote_ids', [])
            get_info(update)
            if user_data['quote_ids']:
                text = "Переход в режим редактирование \"старых\"!\nНапишите мне id цитаты, и я её вычеркну "
                text += "из списка \"использованных\"\n(1 id за раз!)"
                quotes_list = [["clear_all", "/stop"]]
                for quote in user_data['quote_ids']:
                    quotes_list.append([quote])
                quotes_markup = ReplyKeyboardMarkup(quotes_list, one_time_keyboard=False)
                update.message.reply_text(text, reply_markup=quotes_markup)
            else:
                text = "У вас нет \"старых\" цитат!"
                update.message.reply_text(text)
                user_data['job'] = None
                return ConversationHandler.END  
            return 3
        else:
            logging.warning("ERR"+str(user_data['job']))        
   
    def change_quotes(self, bot, update, user_data):
        if user_data['job'] == 3:
            user = get_info(update, "EDIT_QUOTE_REQ")['user']
            user_data['quote_ids'] = user_data.get('quote_ids', [])
            msg = update.message.text.strip()
            answer = "OK"
            if msg == "clear_all":
                user_data['quote_ids'] = []
                update.message.reply_text(answer)
            elif msg in user_data['quote_ids']:
                try:
                    user_data['quote_ids'].remove(msg)
                    quotes_list = [["clear_all", "/stop"]]
                    for quote in user_data['quote_ids']:
                        quotes_list.append([quote])
                    quotes_markup = ReplyKeyboardMarkup(quotes_list, one_time_keyboard=False)    
                    update.message.reply_text(answer, reply_markup=quotes_markup)
                except ValueError:
                    logging.warning("NO_QUOTE"+"|MSG:|"+msg+"|ALL:|"+str(user_data['quote_ids']))
                    answer = "Ошибочка!"
                    update.message.reply_text(answer)
            else:
                answer = "Такого id в списке нет!"
                update.message.reply_text(answer)
            logging.info('EDIT_QUOTE_ANS TO '+user+': '+answer)  
            if not user_data['quote_ids']:
                update.message.reply_text("Список пуст! Выход из режима редактирования списка \"старых\" цитат!",
                                          reply_markup=MARKUP)
                user_data['job'] = None
                return ConversationHandler.END
        else:
            logging.warning("ERR"+str(user_data['job']))        
        pass
   
    def quotes_stop(self, bot, update, user_data):
        user_data['job'] = None
        get_info(update)
        update.message.reply_text("Выход из режима редактирования списка \"старых\" цитат!", reply_markup=MARKUP)
        return ConversationHandler.END  
 
 
    def bash_quote(self, bot, update, user_data):
        user_data['job'] = user_data.get('job', [])
        if not user_data['job']:
            user_data['quote_ids'] = user_data.get('quote_ids', [])
            user = get_info(update, "QUOTE_REQ")['user']
            answer, quote_id = get_quote()
            if quote_id in user_data['quote_ids']:
                answer = "Нет новых цитат!"
            else:
                user_data['quote_ids'] = user_data.get('quote_ids') + [quote_id]
            logging.info('QUOTE_ANS TO '+user+': '+answer)
            update.message.reply_text(answer)  
        pass
 
    def get_last_quotes(self, bot, update, user_data):
        user_data['job'] = user_data.get('job', [])
        if not user_data['job']:        
            quotes = user_data.get('quote_ids', [])
            user = get_info(update, "LAST_QUOTES_REQ")['user']
            if quotes:
                answer = "Список сказанных ранее цитат (я не буду говорить тебе цитату,"
                answer +=  "пока ее id есть в этом списке):\n"
                answer += "\n".join(quotes)
            else:
                answer = "Нет цитат, которые я не буду говорить!"
            logging.info('LAST_QUOTES_ANS TO '+user+': '+answer)
            update.message.reply_text(answer)
            pass
    pass
 

class Weather:
    def __init__(self):
        self.weather = YandexWeather()
        
    def get_weather(self, bot, update):
        location = update.message.location
        user = get_info(update, "WEATHER_REQ <<"+str(location)+">>", location=True)['user']
        answer = self.weather.get_weather(location['longitude'], location['latitude'])
        if answer[0]:
            msg = "Погода ({}):\n{}".format(answer[0], answer[1])
        else:
            msg = "Возникла очень странная ошибка...."
            logging.error("WEATHER_ERR TO "+user+': '+answer[1])
        update.message.reply_text(msg)
        logging.info("WEATHER_ANS TO "+user+': '+msg)
        pass    
    
    def get_weather_by_place(self, bot, update, args):
        place = " ".join(args)
        days = 1
        if args and args[-1].isdigit():
            place = " ".join(args[:-1])
            days = args[-1]
            if int(days) > 7:
                days = "7"
            if int(days) <= 0:
                days = "1"
        
        if not place:
            place = "Москва"
            
        user = get_info(update, "WEATHER_REQ <<PLACE: ["+place+"]>>")['user']
        answer = self.weather.get_weather_by_place(place, days)
        if answer[0]:
            msg = "Погода ({}):\n{}".format(answer[0], answer[1])
        else:
            msg = "Возникла очень странная ошибка...."+answer[1]
            logging.error("WEATHER_ERR TO "+user+': '+answer[1])
        update.message.reply_text(msg)
        logging.info("WEATHER_ANS TO "+user+': '+msg)
        pass
    pass


def get_info(update, data="SENT", write_log=True, location=False):
    msg = update.message
    ans = {"chat": msg.chat,
           "from": msg.from_user,
           "id": msg.from_user['id']}
    
    if location:
        ans['text']=""
        ans['location'] = msg.location
    else:
        ans['location']=""
        ans['text'] = msg.text
        
    nickname = ans['chat'].username
    ans['nickname'] = nickname
    if nickname:
        nickname = " @"+nickname
    else:
        nickname = ""
    user = ""
    if ans['from'].first_name:
        user += ans['from'].first_name
    if ans['from'].last_name:
        user += " "+ans['from'].last_name
    user = "USER: <"+user+" "+nickname
    user += " ("+str(ans['id']) + ")>"
    ans['user'] = user
    data = user+" "+data+": <"+ans['text']+">"
    ans['beaut_info'] = data
    if write_log:
        logging.info(data)
    return ans
   
 
def write_to_log(bot, update):
    get_info(update)
    update.message.reply_text("Saved!")
    pass
 
 
def close_keyboard(bot, update):
    get_info(update)
    update.message.reply_text("Ok", reply_markup=MIN_MARKUP)
    pass
   
   
def start(bot, update):
    info = get_info(update)
    print(info['chat'],info['text'],info['from'])
 
    greeting = "Привет! Я - крутой бот, который может тебе помочь! Посмотри, что я умею:\n"
    greeting += "\n".join(FEATURES)
    update.message.reply_text(greeting, reply_markup=MARKUP)
    pass
 
 
def log_text(bot, update):
    get_info(update)
    pass
 
 
def get_log(bot, update):
    user = get_info(update)
    if user['id'] in MASTERS_IDS:
        update.message.reply_text("Лови!")
        update.message.reply_document(open("TelegramBot.log", 'rb'))
       
    else:
        bot.sendMessage(chat_id=MASTERS_IDS[0], text="Попытка получить лог!")
        bot.sendMessage(chat_id=MASTERS_IDS[0], text=user['beaut_info'])
        update.message.reply_text("У вас нет доступа к этому!")
    pass
 




def main(token):
    updater = Updater(token)
    dp = updater.dispatcher  
    #Classes
    translator_handler = Translator()
    counter_handler = Counter()
    quotes = QuoteGrabber()
    weather = Weather()
    #Conv. handlers:
    translate_handler = ConversationHandler(
        entry_points=[CommandHandler("translate", translator_handler.translate_start, pass_user_data=True)],
        states={
            1: [MessageHandler(Filters.text, translator_handler.translate, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('stop', translator_handler.translate_stop, pass_user_data=True)]
    )    
   
    calc_handler = ConversationHandler(
        entry_points=[CommandHandler("count", counter_handler.count_start, pass_user_data=True)],
        states={
            2: [MessageHandler(Filters.text, counter_handler.count, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('stop', counter_handler.count_stop, pass_user_data=True)]
    )      
   
    quotes_handler = ConversationHandler(
        entry_points=[CommandHandler("change_last_quotes", quotes.quotes_start, pass_user_data=True)],
        states={
            3: [MessageHandler(Filters.text, quotes.change_quotes, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('stop', quotes.quotes_stop, pass_user_data=True)]
    )      
    #Features:
    dp.add_handler(CommandHandler("start", start)) #Greeting
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(CommandHandler("get_log", get_log))
    dp.add_handler(CommandHandler("random_quote", quotes.bash_quote, pass_user_data=True))
    dp.add_handler(CommandHandler("get_last_quotes", quotes.get_last_quotes, pass_user_data=True))
    dp.add_handler(translate_handler)
    dp.add_handler(calc_handler)
    dp.add_handler(quotes_handler)
    #YandexWeather block
    dp.add_handler(MessageHandler(Filters.location, weather.get_weather))
    dp.add_handler(CommandHandler("get_weather", weather.get_weather_by_place, pass_args=True)) #12121
    #*****************************
    dp.add_handler(MessageHandler(Filters.text, write_to_log))
   
    print("STARTED")
    logging.info("Bot started")
    updater.start_polling()
    updater.idle()
    pass
 

if __name__ == '__main__':
    MASTERS_IDS = [403054226, 265801498]
    FEATURES = ["1)Переводить фразы c русского на английский и наоборот! (/translate)",
                "2)Считать за тебя! (/count)",
                "3)Работать с цитатами!"]
   
    reply_keyboard = [['/start', '/close'],
                      ['/count', '/translate'],
                      ["/random_quote", "/get_last_quotes", ],
                      ["/get_weather", "/change_last_quotes"]] #Buttons    
    MARKUP = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    MIN_MARKUP = ReplyKeyboardMarkup([["/start"]], one_time_keyboard=False)
    STOP_MARKUP = ReplyKeyboardMarkup([["/stop"]], one_time_keyboard=False)
   
    response, key = get_key("telegram-bot")
    if response:
        translator = YandexDictionary()
        print("My name: @SupremeSmartBot")
        main(key)
    else:
        print("ERR:", key)
    pass
