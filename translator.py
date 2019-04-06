#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests
from keys import get_key


KEY = get_key("translator")
LANGUAGES = {"ru": "ru-en",
             "en": "en-ru"}
ERR_PHRASE = "Затрудняюсь перевести"


def translate(text, lang):
    url = "https://translate.yandex.net/api/v1.5/tr.json/translate"
    params = {'key': KEY,
              'lang': lang,
              'text': text}
    try:
        response = requests.get(url, params)
        json = response.json()
        if json['code'] == 200:
            return "||".join(json['text'])
    except BaseException:
        pass
    return ERR_PHRASE

#!/usr/bin/python
# -*- coding: utf-8 -*-
def get_lang(text, hint="en,ru"):
    url = "https://translate.yandex.net/api/v1.5/tr.json/detect"
    params = {'key': KEY,
              "text": text,
              "hint": hint}
    try:
        response = requests.get(url, params)
        json = response.json()
        if json['code'] == 200:
            lang = json['lang']
            answer = LANGUAGES[lang]
            return (True, answer)
    except BaseException:
        pass
    return (False, None)


def analyze_and_translate(text):
    lang = get_lang(text)
    if lang[0]:
        return translate(text, lang)
    return ERR_PHRASE