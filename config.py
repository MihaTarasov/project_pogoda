import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

class Config:
    """Конфигурация приложения"""
    # Токены теперь ТОЛЬКО из .env
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
    
    # Настройки API
    WEATHER_API_BASE_URL = 'https://api.openweathermap.org/data/2.5'
    
    # Настройки единиц измерения
    UNITS_MAPPING = {
        'C': {
            'api_units': 'metric',
            'symbol': '°C'
        },
        'F': {
            'api_units': 'imperial',
            'symbol': '°F'
        }
    }