class YandexWeather:
    def __init__(self):
        self.WEATHER_KEY = "KEY"
        
    def get_weather(self, lon, lat):
        return ("[Место или False]", "Хорошая ({};{})".format(str(lon), str(lat)))