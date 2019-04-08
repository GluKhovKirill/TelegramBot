#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup #, Bot #, ReplyKeyboardRemove
from keys import get_key
from translator import TheTranslator
from count import MathExecutor


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
    
    
def close_keyboard(bot, update):
    get_info(update)
    update.message.reply_text("Ok", reply_markup=MIN_MARKUP)
    pass
    
    
def start(bot, update):
    print("D",type(bot), type(update), update)
    #bot.send_message(chat_id=bot.message.chat_id, text="HI")
    info = get_info(update)
    print(info['chat'],info['text'],info['from'])

    greeting = "Привет! Я - крутой бот, который может тебе помочь! Посмотри, что я умею:\n"
    greeting += "\n".join(FEATURES)
    update.message.reply_text(greeting, reply_markup=MARKUP)
    pass


def translate_start(bot, update):
    get_info(update)
    text = "Переход в режим переводчика!\nЕсли написать мне фразу на русском, я переведу "
    text += "её на английский и наоборот.\nДля выхода используйте /stop"
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
    text += "\n(Не больше 1 операнда за раз!)\n(И, пожалуйста, отделяйте числа от операндов пробелами)"
    update.message.reply_text(text, reply_markup=STOP_MARKUP)
    return 1


def count(bot, update):
    user = get_info(update, "COUNT_REQ")['user']
    data = update.message.text.split()
    if 'pi' in data: 
        data[1] = 'pi'
    if 'e' in data:
        data[1] = 'e'
    answer = MathExecutor(data[0], data[1], data[2]).execute()
    logging.info('COUNT_ANS TO '+user+': '+answer)
    update.message.reply_text(answer)    
    pass


def count_stop(bot, update):
    get_info(update)
    update.message.reply_text("Выход из режима вычислителя!", reply_markup=MARKUP)
    return ConversationHandler.END    


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
    #Features:
    dp.add_handler(CommandHandler("start", start)) #Greeting
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(CommandHandler("get_log", get_log))
    dp.add_handler(translate_handler)
    dp.add_handler(calc_handler)
    '''
    text_handler = MessageHandler(Filters.text, echo)
    dp.add_handler(text_handler)
    '''
    
    print("STARTED")
    logging.info("Bot started")
    updater.start_polling()
    updater.idle()
    pass


if __name__ == '__main__':
    MASTERS_IDS = [403054226, 265801498]
    FEATURES = ["1)Переводить фразы c русского на английский и наоборот! (/translate)",
                "2)Считать за тебя! (/count)"]
    
    reply_keyboard = [['/count', '/translate'],
                      ['/start', '/close'],
                      ["/get_log"]] #Buttons    
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