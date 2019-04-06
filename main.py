#!/usr/bin/python
# -*- coding: utf-8 -*-


import logging
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup #, ReplyKeyboardRemove
from keys import get_key
from translator import analyze_and_translate


logging.basicConfig(level=logging.DEBUG, filename="TelegramBot.log",
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') #TODO: level=loging.INFO


def close_keyboard(bot, update):
    update.message.reply_text("Ok", reply_markup=MIN_MARKUP)
    pass
  
  
def start(bot, update):
    print(bot, update) #TODO: remove
    greeting = "Привет! Я - крутой бот, который может тебе помочь! Посмтори, что я умею:\n"
    greeting += "\n".join(FEATURES)
    update.message.reply_text(greeting, reply_markup=MARKUP)
    pass


def translate_start(bot, update):
    text = "Переход в режим переводчика!\nЕсли написать мне фразу на русском - я переведу "
    text += "её на английский и наоборот.\nДля выхода используйте /stop"
    update.message.reply_text(text, reply_markup=STOP_MARKUP)
    return 1


def translate(bot, update):
    answer = analyze_and_translate(update.message.text)
    update.message.reply_text(answer)
    pass


def translate_stop (bot, update):
    update.message.reply_text("Выход из режима переводчика!", reply_markup=MARKUP)
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
    
    
    #Features:
    dp.add_handler(CommandHandler("start", start)) #Greeting
    dp.add_handler(CommandHandler("close", close_keyboard))
    dp.add_handler(translate_handler)
    
    
    '''
    text_handler = MessageHandler(Filters.text, echo)
    dp.add_handler(text_handler)
    '''
    
    print("STARTED")
    logging.info("Bot started")
    updater.start_polling()
    updater.idle()
    pass


if(__name__ == '__main__'):
    FEATURES = ["1)Переводить фразы c русского на английский и наоборот! (/translate)",
                "2)Считать за тебя! (/count)"]
    
    
    reply_keyboard = [['/count', '/translate'],
                      ['/start', '/close']]
    
    
    #Buttons
    MARKUP = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    MIN_MARKUP = ReplyKeyboardMarkup([["/start"]], one_time_keyboard=False)
    STOP_MARKUP = ReplyKeyboardMarkup([["/stop"]], one_time_keyboard=False)
    response, key = get_key("telegram-bot")
    if(response):
        print("My name: @SupremeSmartBot")
        main(key)
    else: 
        print("ERR:", key)
