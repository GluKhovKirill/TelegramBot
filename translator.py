#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from keys import get_key
 
 
class YandexDictionary:
    #Реализовано с помощью сервиса «API «Яндекс.Словарь» с активной гиперссылкой на страницу http://api.yandex.ru/dictionary/
    def __init__(self):
        self.DICT_KEY = get_key("dictionary")[1]
        self.TRANSLATOR_KEY = get_key("translator")[1]
        self.LANGUAGES = {"ru": "ru-en",
                          "en": "en-ru"}
        self.ERR_PHRASE = "Затрудняюсь перевести"
       
    def translate_translator(self, text, lang):
        url = "https://translate.yandex.net/api/v1.5/tr.json/translate"
        params = {'key': self.TRANSLATOR_KEY,
                  'lang': lang,
                  'text': text}
        try:
            response = requests.get(url, params)
            json = response.json()
            if json['code'] == 200:
                return "\n".join(json['text'])
        except BaseException:
            pass
        return self.ERR_PHRASE
   
    def translate_dict(self, text, lang):
        url = "https://dictionary.yandex.net/api/v1/dicservice.json/lookup"
        params = {'key': self.DICT_KEY,
                  'lang': lang,
                  'text': text}
        try:
            response = requests.get(url, params)
            global json
            json = response.json()['def']
            if json:
                json = json[0]
                answer = [syn['text'] for syn in json['tr']]
                return "\n".join(answer)
            else:
                return self.translate_translator(text, lang)
        except BaseException:
            pass
        return self.ERR_PHRASE        
   
    def get_lang(self, text, hint="en,ru"):
        url = "https://translate.yandex.net/api/v1.5/tr.json/detect"
        params = {'key': self.TRANSLATOR_KEY,
                  "text": text,
                  "hint": hint}
        try:
            response = requests.get(url, params)
            json = response.json()
            if json['code'] == 200:
                lang = json['lang']
                answer = self.LANGUAGES[lang]
                return (True, answer)
        except BaseException:
            pass
        return (False, None)    
   
    def analyze_and_translate(self, text):
        lang = self.get_lang(text)
        if(lang[0]):
            return self.translate_dict(text, lang)
        return self.ERR_PHRASE
