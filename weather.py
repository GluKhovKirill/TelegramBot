class YandexWeather:
    def __init__(self):
        self.WEATHER_KEY = "KEY"
        self.ERR_PHRASE = "Затрудняюсь определить погоду"
        
    def get_weather(self, lon, lat):
        return ("[Место или False]", "Хорошая ({};{})".format(str(lon), str(lat)))
    
    def get_weather_by_place(self, place):
        return (place, "Хорошая")