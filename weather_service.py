import requests
from datetime import datetime, timedelta
from config import Config


class WeatherService:
    """Сервис для работы с погодными данными"""
    
    def __init__(self, api_key=Config.WEATHER_API_KEY):
        self.api_key = api_key
        self.base_url = Config.WEATHER_API_BASE_URL
    
    def get_current_weather(self, city, units='C'):
        """Получение текущей погоды"""
        api_units = Config.UNITS_MAPPING[units]['api_units']
        url = f'{self.base_url}/weather?q={city}&appid={self.api_key}&units={api_units}&lang=ru'
        response = requests.get(url)
        return response.json()
    
    def get_forecast(self, city, units='C'):
        """Получение прогноза на 5 дней"""
        api_units = Config.UNITS_MAPPING[units]['api_units']
        url = f'{self.base_url}/forecast?q={city}&appid={self.api_key}&units={api_units}&lang=ru'
        response = requests.get(url)
        return response.json()
    
    @staticmethod
    def get_day_name(date_obj):
        """Получение названия дня"""
        today = datetime.now().date()
        
        if date_obj == today:
            return "Сегодня"
        elif date_obj == today + timedelta(days=1):
            return "Завтра"
        elif date_obj == today + timedelta(days=2):
            return "Послезавтра"
        else:
            days_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
            return days_ru[date_obj.weekday()]
    
    @staticmethod
    def format_forecast_response(forecast_data, city, units):
        """Форматирование прогноза для ответа"""
        if forecast_data.get('cod') == '200':
            forecasts = []
            today = datetime.now().date()
            
            for item in forecast_data['list']:
                forecast_time = datetime.fromtimestamp(item['dt'])
                
                if 11 <= forecast_time.hour <= 13:
                    forecasts.append({
                        'date': forecast_time.date(),
                        'temp': item['main']['temp'],
                        'weather': item['weather'][0]['description'].capitalize(),
                        'day_name': WeatherService.get_day_name(forecast_time.date())
                    })
            
            temp_unit = Config.UNITS_MAPPING[units]['symbol']
            reply = f"📅 Прогноз на 5 дней для {city} ({temp_unit}):\n\n"
            
            for i, forecast in enumerate(forecasts[:5]):
                reply += f"{forecast['day_name']}:\n"
                reply += f"  {forecast['weather']}, {forecast['temp']}{temp_unit}\n\n"
            
            return reply
        return None