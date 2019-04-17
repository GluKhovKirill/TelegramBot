#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup #, Bot #, ReplyKeyboardRemove
from keys import get_key
from translator import TheTranslator
from count import MathExecutor
from bash import get_quote


logging.basicConfig(level=logging.INFO, filename="TelegramBot.log",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') #TODO: level=loging.INFO


def get_info(update, data="SENT", write_log=True):
    msg = update.message
    ans = {"chat": msg.chat, 
           "text": msg.text, 
           "from": msg.from_user,
           "id": msg.from_user['id']}
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
    data = user+": <"+ans['text']+">"
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


def translate_start(bot, update):
    get_info(update)
    text = "Переход в режим переводчика!\nЕсли написать мне фразу на русском, я переведу "
    text += "её на английский и наоборот.\nДля выхода используйте /stop\n"
    text += '(Переведено сервисом "Яндекс.Переводчик"\n'
    text += "https://translate.yandex.ru )."
    update.message.reply_text(text, reply_markup=STOP_MARKUP)
    return 1


def translate(bot, update):
    user = get_info(update, "TRANSLATOR_REQ")['user']
    answer = translator.analyze_and_translate(update.message.text)
    logging.info('TRANSLATOR_ANS TO '+user+': '+answer)
    update.message.reply_text(answer)
    pass


def translate_stop(bot, update):
    get_info(update)
    update.message.reply_text("Выход из режима переводчика!", reply_markup=MARKUP)
    return ConversationHandler.END


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


def count_start(bot, update):
    get_info(update)
    text = "Переход в режим вычислителя!\nНапишите мне пример, и я его вычислю"
    text += "\n(Не больше 1 операнда за раз!)"
    update.message.reply_text(text, reply_markup=STOP_MARKUP)
    return 1


def count(bot, update):
    user = get_info(update, "COUNT_REQ")['user']
    msg = update.message.text.replace(" ", "")
    n = 0
    data = ["", "", ""]
    last_symbol = msg[0]
    for symbol in msg:
        if symbol.isdigit() != last_symbol.isdigit():
            n += 1
        data[n] += symbol
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
    pass


def count_stop(bot, update):
    get_info(update)
    update.message.reply_text("Выход из режима вычислителя!", reply_markup=MARKUP)
    return ConversationHandler.END    


def quotes_start(bot, update, user_data):
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
        return ConversationHandler.END  
    return 1


def change_quotes(bot, update, user_data):
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
        return ConversationHandler.END
    pass


def quotes_stop(bot, update):
    get_info(update)
    update.message.reply_text("Выход из режима редактирования списка \"старых\" цитат!", reply_markup=MARKUP)
    return ConversationHandler.END   


def bash_quote(bot, update, user_data):
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


def log_text(bot, update):
    get_info(update)
    pass


def get_last_quotes(bot, update, user_data):
    quotes = user_data.get('quote_ids', [])
    if quotes:
        answer = "Список сказанных ранее цитат (я не буду говорить тебе цитату,"
        answer +=  "пока ее id есть в этом списке):\n"
        answer += "\n".join(quotes)
    else:
        answer = "Нет цитат, которые я не буду говорить!"
    update.message.reply_text(answer)
    pass


def main(token):
    updater = Updater(token)
    dp = updater.dispatcher  
    #Conv. handlers:
    translate_handler = ConversationHandler(
        entry_points=[CommandHandler("translate", translate_start)],
        states={
            1: [MessageHandler(Filters.text, translate)]
        },
        fallbacks=[CommandHandler('stop', translate_stop)]
    )    
    
    calc_handler = ConversationHandler(
        entry_points=[CommandHandler("count", count_start)],
        states={
            1: [MessageHandler(Filters.text, count)]
        },
        fallbacks=[CommandHandler('stop', count_stop)]
    )      
    
    quotes_handler = ConversationHandler(
        entry_points=[CommandHandler("change_last_quotes", quotes_start, pass_user_data=True)],
        states={
            1: [MessageHandler(Filters.text, change_quotes, pass_user_data=True)]
        },
        fallbacks=[CommandHandler('stop', quotes_stop)]
    )      
    #Features:
    dp.add_handler(CommandHandler("start", start)) #Greeting
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(CommandHandler("get_log", get_log))
    dp.add_handler(CommandHandler("random_quote", bash_quote, pass_user_data=True))
    dp.add_handler(CommandHandler("get_last_quotes", get_last_quotes, pass_user_data=True))
    dp.add_handler(translate_handler)
    dp.add_handler(calc_handler)
    dp.add_handler(quotes_handler)
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
                "МНОГОЕ!.."]
    
    reply_keyboard = [['/start', '/close'],
                      ['/count', '/translate'],
                      ["/random_quote", "/get_last_quotes", ],
                      ["/get_log", "/change_last_quotes"]] #Buttons    
    MARKUP = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    MIN_MARKUP = ReplyKeyboardMarkup([["/start"]], one_time_keyboard=False)
    STOP_MARKUP = ReplyKeyboardMarkup([["/stop"]], one_time_keyboard=False)
    
    response, key = get_key("telegram-bot")
    if response:
        translator = TheTranslator()
        print("My name: @SupremeSmartBot")
        main(key)
    else: 
        print("ERR:", key)
