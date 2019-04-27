#!/usr/bin/python
# -*- coding: utf-8 -*-


import requests
from keys import get_key


class YandexWeather:
    def __init__(self):
        self.ERR_PHRASE = "Затрудняюсь определить погоду"
        self.CONDITIONS = {'clear': "ясно",
                           'partly-cloudy': 'малооблачно',
                           'cloudy': 'облачно с прояснениями',
                           'overcast': 'пасмурно',
                           'partly-cloudy-and-light-rain': 'небольшой дождь',
                           'partly-cloudy-and-rain': 'дождь',
                           'overcast-and-rain': 'сильный дождь',
                           'overcast-thunderstorms-with-rain': 'сильный дождь, гроза',
                           'cloudy-and-light-rain': 'небольшой дождь',
                           'overcast-and-light-rain': 'небольшой дождь',
                           'cloudy-and-rain': 'дождь',
                           'overcast-and-wet-snow': 'дождь со снегом',
                           'partly-cloudy-and-light-snow': 'небольшой снег',
                           'partly-cloudy-and-snow': 'снег',
                           'overcast-and-snow': 'снегопад',
                           'cloudy-and-light-snow': 'небольшой снег',
                           'overcast-and-light-snow': 'небольшой снег',
                           'cloudy-and-snow': 'снег'}
        key = get_key("weather")
        if key[0]:
            self.WEATHER_KEY = key[1]
        else:
            print("WEATHER: KEY ERR!!")
            return "ERR"
       
    def get_weather(self, lon, lat, days=1):
        #внешняя
        url = "https://api.weather.yandex.ru/v1/forecast"
        params = {'lat': lat,
                  'lon': lon,
                  "limit": str(days)}
        try:
            response = requests.get(url, params, headers={"X-Yandex-API-Key":self.WEATHER_KEY})
            json = response.json()
            forecasts = json['forecasts']
            answer = []
            for forecast in forecasts[:int(days)]:
                date = forecast['date']
                sun = forecast['sunrise'], forecast['sunset']
               
                parts = forecast['parts']
                the_morning = [parts['morning']['temp_avg'], self.CONDITIONS[parts['morning']['condition']],
                           parts['morning']['wind_speed'], parts['morning']['humidity'], parts['morning']['pressure_mm']]
                the_day = [parts['day']['temp_avg'], self.CONDITIONS[parts['day']['condition']],
                           parts['day']['wind_speed'], parts['day']['humidity'], parts['day']['pressure_mm']]
                the_evening = [parts['evening']['temp_avg'], self.CONDITIONS[parts['evening']['condition']],
                           parts['evening']['wind_speed'], parts['evening']['humidity'], parts['evening']['pressure_mm']]
               
                day = "{}: восход в {}, закат - в {}. ".format(date, sun[0], sun[1])
                day += "Утром: {}°C, {}, ветер: {}м/с, влажность: {}%, давление: {}мм рт. ст.; " .format(*the_morning)
                day += "Днём: {}°C, {}, ветер: {}м/с, влажность: {}%, давление: {}мм рт. ст.; ".format(*the_day)
                day += " Вечером: {}°C, {}, ветер: {}м/с, влажность: {}%, давление: {}мм рт. ст..".format(*the_evening)
                answer.append(day)
                #print(day)
            answer = "\n***********\n".join(answer)
            #answer += "\nЯндекс.Погода {}".format(json['info']['url'])
            return (True, answer)# answer) #TODO: remove
        except BaseException:
            pass
        return (False, self.ERR_PHRASE)
    
    
    def get_weather_by_place(self, place, days=1):
        #https://geocode-maps.yandex.ru/1.x/?geocode=Москва&format=json
        url = "https://geocode-maps.yandex.ru/1.x/"
        params = {"format": "json",
                  "geocode": place,}
        try:
            response = requests.get(url, params)
            json = response.json()['response']['GeoObjectCollection']['featureMember']
            if json:
                lon, lat = json[0]['GeoObject']['Point']['pos'].split()
                return self.get_weather(lon, lat, days)
        except BaseException:
            pass
        return (False, self.ERR_PHRASE)
