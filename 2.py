import telebot
import requests

TOKEN = '8599848575:AAF0aUSBXMDKZbJg189Ve7Se-jKtW6BFNrI'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет, я твой телеграм бот! Теперь я умею показывать погоду по запросу, но скоро я стану еще лучше!")


@bot.message_handler(func=lambda message: message.text.startswith('/pogoda'))
def handle_pogoda(message):
    text = message.text.strip()
    
    if text == '/pogoda':
        bot.reply_to(message, "Напиши город после команды /pogoda\n\nПример: /pogoda Москва")
        return
    
    try:
        city = text[8:].strip()  
        
        if not city:
            bot.reply_to(message, "Напиши город после команды!\nПример: /pogoda Москва")
            return
            
        api_key = '3d9de74844d28377e81415151cbe6a66'
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru'
        
        response = requests.get(url).json()
        
        if response['cod'] == 200:
            weather = response['weather'][0]['description']
            temp = response['main']['temp']
            
            bot.reply_to(message, f"Погода в {city}:\n{weather}, {temp}°C")
        else:
            bot.reply_to(message, f"Город '{city}' не найден")
            
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

if __name__ == '__main__':
    print("Бот запущен!")
    bot.polling()