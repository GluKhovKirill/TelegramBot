#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from keys import get_key


class TheTranslator:
    def __init__(self):
        self.KEY = get_key("translator")
        self.LANGUAGES = {"ru": "ru-en",
                     "en": "en-ru"}
        self.ERR_PHRASE = "Затрудняюсь перевести"


    def translate(self, text, lang):
        url = "https://translate.yandex.net/api/v1.5/tr.json/translate"
        params = {'key': self.KEY,
                  'lang': lang,
                  'text': text}
        try:
            response = requests.get(url, params)
            json = response.json()
            if json['code'] == 200:
                return "||".join(json['text'])
        except BaseException:
            pass
        return self.ERR_PHRASE
        
        
    def get_lang(self, text, hint="en,ru"):
        url = "https://translate.yandex.net/api/v1.5/tr.json/detect"
        params = {'key': self.KEY,
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
            return self.translate(text, lang)
        return self.ERR_PHRASE
