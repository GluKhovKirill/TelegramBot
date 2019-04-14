#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests


url = "https://bash.im/forweb/?u"
headers = {'User-agent': 'Mozilla/5.0'}


def get_quote():
    try:
        response = requests.get(url, headers=headers)
        text = response.text.split("\n")[3]
        quote = text[text.find("quote"):]
        quote = quote[quote.find(">")+1:quote.find("<")]
        text = text[text.find("/header")+9:text.rfind("footer style")]
        text = text[text.find(">")+1:text.rfind("/div")]
        text = text[:text.rfind("<")]
        text = text.replace('.*1em 0;">', "").replace("<' %+ '/div>.*", "")
        text = text.replace("<' %+ 'br.?.?>", "\n").replace("&quot;", '"')
        text = text.replace("&lt;", '<').replace("&gt;", '>')
        text = text.replace("&#39;", "'").replace("<\' + \'br>", "\n")
        text = text.replace("<' + 'br />", "\n")
        return text+"\n("+quote+")"
    except BaseException:
        return "Цитаты кончились!"