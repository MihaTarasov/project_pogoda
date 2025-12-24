import telebot
from config import Config
from bot_handlers import BotHandlers
from weather_service import WeatherService


def main():
    """Точка входа в приложение"""
    # Инициализация бота
    bot = telebot.TeleBot(Config.BOT_TOKEN)
    
    # Инициализация сервиса погоды
    weather_service = WeatherService()
    
    # Инициализация обработчиков
    BotHandlers(bot, weather_service)
    
    # Запуск бота
    print("Бот запущен!")
    bot.polling()


if __name__ == '__main__':
    main()