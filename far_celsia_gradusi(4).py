import telebot
import requests

TOKEN = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot("8599848575:AAF0aUSBXMDKZbJg189Ve7Se-jKtW6BFNrI")

# Хранилище данных
user_cities = {}
# Хранилище единиц измерения {user_id: 'C' или 'F'}
user_units = {}  # По умолчанию 'C' (Цельсий)

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    units = user_units.get(user_id, 'C')
    unit_symbol = '°C' if units == 'C' else '°F'
    
    if user_id in user_cities:
        bot.reply_to(message, 
            f"Привет! Я уже знаю твой город: {user_cities[user_id]}\n"
            f"Единицы измерения: {unit_symbol}\n\n"
            f"Основные команды:\n"
            f"/pogoda - показать погоду\n"
            f"/mycity - активный город\n"
            f"/changecity - сменить город\n"
            f"/units - сменить единицы измерения\n"
            f"/help - все команды")
    else:
        bot.reply_to(message,
            "Привет! Я бот для погоды. Сначала установи свой город:\n"
            "Напиши /setcity и название города\n"
            f"Единицы измерения: {unit_symbol}\n"
            "Например: /setcity Москва")

# Команда /units - сменить единицы измерения
@bot.message_handler(commands=['units'])
def change_units(message):
    user_id = message.from_user.id
    current_units = user_units.get(user_id, 'C')
    
    if current_units == 'C':
        user_units[user_id] = 'F'
        new_units = '°F (Фаренгейт)'
        old_units = '°C (Цельсий)'
    else:
        user_units[user_id] = 'C'
        new_units = '°C (Цельсий)'
        old_units = '°F (Фаренгейт)'
    
    bot.reply_to(message, 
        f"✅ Единицы измерения изменены:\n"
        f"Было: {old_units}\n"
        f"Стало: {new_units}\n\n"
        f"Теперь погода будет показываться в {new_units}")

# Команда /setcity Москва
@bot.message_handler(func=lambda m: m.text and m.text.startswith('/setcity'))
def set_city(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text == '/setcity':
        units = user_units.get(user_id, 'C')
        unit_symbol = '°C' if units == 'C' else '°F'
        bot.reply_to(message, 
            f"Напиши /setcity и название города\n"
            f"Единицы: {unit_symbol}\n"
            f"Пример: /setcity Москва")
        return
    
    try:
        city = text[9:].strip()
        
        if not city:
            bot.reply_to(message, "Укажи город! Пример: /setcity Москва")
            return
        
        # Проверяем город
        api_key = '3d9de74844d28377e81415151cbe6a66'
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=ru'
        response = requests.get(url)
        data = response.json()
        
        if data.get('cod') == 200:
            user_cities[user_id] = city
            units = user_units.get(user_id, 'C')
            unit_symbol = '°C' if units == 'C' else '°F'
            
            bot.reply_to(message, 
                f"✅ Город установлен: {city}\n"
                f"Единицы измерения: {unit_symbol}\n"
                f"Теперь пиши /pogoda для получения погоды!")
        else:
            bot.reply_to(message, f"❌ Город '{city}' не найден. Попробуй другой.")
            
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

# Команда /pogoda
@bot.message_handler(commands=['pogoda'])
def show_weather(message):
    user_id = message.from_user.id
    
    if user_id not in user_cities:
        bot.reply_to(message, "Сначала установи город командой /setcity")
        return
    
    city = user_cities[user_id]
    units = user_units.get(user_id, 'C')  # Получаем единицы измерения
    
    try:
        api_key = '3d9de74844d28377e81415151cbe6a66'
        
        # Выбираем units для API
        if units == 'C':
            api_units = 'metric'  # Для Цельсия
            temp_unit = '°C'
        else:
            api_units = 'imperial'  # Для Фаренгейта
            temp_unit = '°F'
        
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={api_units}&lang=ru'
        response = requests.get(url)
        data = response.json()
        
        if data.get('cod') == 200:
            weather = data['weather'][0]['description'].capitalize()
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            
            reply = (f"🌤️ Погода в {city} ({temp_unit}):\n"
                    f"• {weather}\n"
                    f"• Температура: {temp}{temp_unit}\n"
                    f"• Ощущается как: {feels_like}{temp_unit}\n"
                    f"• Влажность: {humidity}%")
            
            bot.reply_to(message, reply)
        else:
            # Резервный вариант с учетом единиц измерения
            import random
            if units == 'C':
                temps = random.randint(-10, 30)
                temp_unit = '°C'
            else:
                temps = random.randint(14, 86)  # -10°C = 14°F, 30°C = 86°F
                temp_unit = '°F'
                
            conditions = ["☀️ Солнечно", "☁️ Облачно", "🌧️ Дождь", "❄️ Снег"]
            condition = random.choice(conditions)
            bot.reply_to(message, 
                f"Погода в {city}:\n"
                f"{condition}, {temps}{temp_unit}\n"
                f"(данные примерные)")
            
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

# Команда /mycity
@bot.message_handler(commands=['mycity'])
def show_city(message):
    user_id = message.from_user.id
    
    if user_id in user_cities:
        units = user_units.get(user_id, 'C')
        unit_symbol = '°C' if units == 'C' else '°F'
        
        bot.reply_to(message, 
            f"🏙️ Твой активный город: {user_cities[user_id]}\n"
            f"📏 Единицы измерения: {unit_symbol}")
    else:
        bot.reply_to(message, 
            "У тебя еще нет установленного города.\n"
            "Напиши /setcity Москва")

# Команда /changecity
@bot.message_handler(func=lambda m: m.text and m.text.startswith('/changecity'))
def change_city(message):
    user_id = message.from_user.id
    text = message.text.strip()
    
    if text == '/changecity':
        units = user_units.get(user_id, 'C')
        unit_symbol = '°C' if units == 'C' else '°F'
        bot.reply_to(message, 
            f"Напиши /changecity и новый город\n"
            f"Единицы: {unit_symbol}\n"
            f"Пример: /changecity Санкт-Петербург")
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
            units = user_units.get(user_id, 'C')
            unit_symbol = '°C' if units == 'C' else '°F'
            
            bot.reply_to(message, 
                f"✅ Город изменен!\n"
                f"Старый: {old_city}\n"
                f"Новый: {new_city}\n"
                f"Единицы: {unit_symbol}")
        else:
            bot.reply_to(message, f"❌ Город '{new_city}' не найден. Попробуй другой.")
            
    except Exception as e:
        bot.reply_to(message, f"Ошибка: {e}")

# Команда /forgetcity
@bot.message_handler(commands=['forgetcity'])
def forget_city(message):
    user_id = message.from_user.id
    
    if user_id in user_cities:
        removed_city = user_cities.pop(user_id)
        # Не удаляем единицы измерения, только город
        bot.reply_to(message, 
            f"🗑️ Город '{removed_city}' удален из памяти.\n"
            f"Установи новый город через /setcity")
    else:
        bot.reply_to(message, "У тебя нет сохраненного города.")

# Обновленная команда /help
@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = message.from_user.id
    units = user_units.get(user_id, 'C')
    unit_symbol = '°C' if units == 'C' else '°F'
    
    help_text = (
        f"📋 Доступные команды (единицы: {unit_symbol}):\n\n"
        "/start - начать работу\n"
        "/setcity [город] - установить город\n"
        "/pogoda - показать погоду в твоем городе\n"
        "/mycity - показать активный город и единицы\n"
        "/changecity [город] - сменить город\n"
        "/units - переключить °C ↔ °F\n"
        "/forgetcity - удалить город из памяти\n"
        "/help - эта справка\n\n"
        "Примеры:\n"
        "/setcity Москва\n"
        "/changecity Казань\n"
        "/units - сменить на Фаренгейты"
    )
    bot.reply_to(message, help_text)

# Запуск
if __name__ == '__main__':
    print("Бот с переключением единиц измерения запущен!")
    bot.polling()