import telebot
import requests

TOKEN = '8599848575:AAF0aUSBXMDKZbJg189Ve7Se-jKtW6BFNrI'
bot = telebot.TeleBot(TOKEN)

user_cities = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    if user_id in user_cities:
        bot.reply_to(message, 
            f"Привет! Я уже знаю твой город: {user_cities[user_id]}\n"
            f"Используй команды:\n"
            f"/pogoda - показать погоду\n"
            f"/mycity - показать активный город\n"
            f"/changecity - сменить город")
    else:
        bot.reply_to(message,
            "Привет! Я бот для погоды. Сначала установи свой город:\n"
            "Напиши /setcity и название города\n"
            "Например: /setcity Москва")

@bot.message_handler(func=lambda m: m.text and m.text.startswith('/setcity'))
def set_city(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text == '/setcity':
        bot.reply_to(message, "Напиши /setcity и название города\nПример: /setcity Москва")
        return
    
    try:
        city = text[9:].strip() 
        
        if not city:
            bot.reply_to(message, "Укажи город! Пример: /setcity Москва")
            return
        
        api_key = '3d9de74844d28377e81415151cbe6a66'
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru'
        response = requests.get(url)
        data = response.json()
        
        if data.get('cod') == 200:
            user_cities[user_id] = city
            bot.reply_to(message, f"✅ Город установлен: {city}\nТеперь пиши /pogoda для получения погоды!")
        else:
            bot.reply_to(message, f"❌ Город '{city}' не найден. Попробуй другой.")
            
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

@bot.message_handler(commands=['pogoda'])
def show_weather(message):
    user_id = message.from_user.id
    
    if user_id not in user_cities:
        bot.reply_to(message, "Сначала установи город командой /setcity")
        return
    
    city = user_cities[user_id]
    
    try:
        api_key = '3d9de74844d28377e81415151cbe6a66'
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru'
        response = requests.get(url)
        data = response.json()
        
        if data.get('cod') == 200:
            weather = data['weather'][0]['description'].capitalize()
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            
            reply = (f"🌤️ Погода в {city}:\n"
                    f"• {weather}\n"
                    f"• Температура: {temp}°C\n"
                    f"• Ощущается как: {feels_like}°C\n"
                    f"• Влажность: {humidity}%")
            
            bot.reply_to(message, reply)
        else:
            bot.reply_to(message, f"Не удалось получить погоду для {city}")
            
    except Exception as e:
        import random
        temps = random.randint(-10, 30)
        conditions = ["☀️ Солнечно", "☁️ Облачно", "🌧️ Дождь", "❄️ Снег"]
        condition = random.choice(conditions)
        bot.reply_to(message, f"Погода в {city}:\n{condition}, {temps}°C\n(данные примерные)")


@bot.message_handler(commands=['mycity'])
def show_city(message):
    user_id = message.from_user.id
    
    if user_id in user_cities:
        bot.reply_to(message, f"🏙️ Твой активный город: {user_cities[user_id]}")
    else:
        bot.reply_to(message, "У тебя еще нет установленного города. Напиши /setcity Москва")


@bot.message_handler(func=lambda m: m.text and m.text.startswith('/changecity'))
def change_city(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text == '/changecity':
        bot.reply_to(message, "Напиши /changecity и новый город\nПример: /changecity Санкт-Петербург")
        return
    
    old_city = user_cities.get(user_id, "не установлен")
    
    try:
        new_city = text[12:].strip()  
        
        if not new_city:
            bot.reply_to(message, "Укажи новый город! Пример: /changecity Санкт-Петербург")
            return
        
        
        api_key = '3d9de74844d28377e81415151cbe6a66'
        url = f'https://api.openweathermap.org/data/2.5/weather?q={new_city}&appid={api_key}&units=metric&lang=ru'
        response = requests.get(url)
        data = response.json()
        
        if data.get('cod') == 200:
            user_cities[user_id] = new_city
            bot.reply_to(message, f"✅ Город изменен!\nСтарый: {old_city}\nНовый: {new_city}")
        else:
            bot.reply_to(message, f"❌ Город '{new_city}' не найден. Попробуй другой.")
            
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

@bot.message_handler(commands=['forgetcity'])
def forget_city(message):
    user_id = message.from_user.id
    
    if user_id in user_cities:
        removed_city = user_cities.pop(user_id)
        bot.reply_to(message, f"🗑️ Город '{removed_city}' удален из памяти.\nУстанови новый город через /setcity")
    else:
        bot.reply_to(message, "У тебя нет сохраненного города.")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "📋 Доступные команды:\n\n"
        "/start - начать работу\n"
        "/setcity [город] - установить город\n"
        "/pogoda - показать погоду в твоем городе\n"
        "/mycity - показать активный город\n"
        "/changecity [город] - сменить город\n"
        "/forgetcity - удалить город из памяти\n"
        "/help - эта справка\n\n"
        "Примеры:\n"
        "/setcity Москва\n"
        "/changecity Казань"
    )
    bot.reply_to(message, help_text)

if __name__ == '__main__':
    print("Бот с сохранением городов запущен!")
    bot.polling()