from telebot import types
import telebot
import requests
from datetime import datetime, timedelta


TOKEN = 'YOUR_BOT_TOKEN'
bot = telebot.TeleBot("8599848575:AAF0aUSBXMDKZbJg189Ve7Se-jKtW6BFNrI")

# Хранилище данных
user_cities = {}

# Хранилище единиц измерения {user_id: 'C' или 'F'}
user_units = {}

def get_main_keyboard():
    """Главная клавиатура с 4 кнопками"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn1 = types.KeyboardButton('🌤️ Погода сейчас')
    btn2 = types.KeyboardButton('📅 Прогноз на 5 дней')
    btn3 = types.KeyboardButton('🏙️ Мой город')
    btn4 = types.KeyboardButton('⚙️ Настройки')
    
    keyboard.add(btn1, btn2, btn3, btn4)
    return keyboard

def get_settings_keyboard():
    """Клавиатура настроек"""
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    btn1 = types.KeyboardButton('📋 Справка')
    btn2 = types.KeyboardButton('✏️ Изменить город')
    btn3 = types.KeyboardButton('🌡️ Единицы измерения')
    btn4 = types.KeyboardButton('⬅️ Назад')
    
    keyboard.add(btn1, btn2, btn3, btn4)
    return keyboard

# Обновляем команду /start чтобы показывала клавиатуру
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    units = user_units.get(user_id, 'C')
    unit_symbol = '°C' if units == 'C' else '°F'
    
    if user_id in user_cities:
        bot.send_message(
            message.chat.id,
            f"Привет! Я уже знаю твой город: {user_cities[user_id]}\n"
            f"Единицы измерения: {unit_symbol}\n\n"
            f"Используй кнопки ниже или команды:",
            reply_markup=get_main_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id,
            "Привет! Я бот для погоды. Сначала установи свой город:\n"
            "Напиши /setcity и название города\n"
            f"Единицы измерения: {unit_symbol}\n"
            "Например: /setcity Москва",
            reply_markup=get_main_keyboard()
        )


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

@bot.message_handler(commands=['forecast'])
def show_forecast(message):
    user_id = message.from_user.id
    
    if user_id not in user_cities:
        bot.reply_to(message, "Сначала установи город командой /setcity")
        return
    
    city = user_cities[user_id]
    units = user_units.get(user_id, 'C')
    
    api_key = '3d9de74844d28377e81415151cbe6a66'
    
    # Выбираем units для API
    if units == 'C':
        api_units = 'metric'
        temp_unit = '°C'
    else:
        api_units = 'imperial'
        temp_unit = '°F'
    
    # Запрос прогноза на 5 дней 
    url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units={api_units}&lang=ru'
    response = requests.get(url)
    data = response.json()
    
    if data.get('cod') == '200':
        # Берем прогноз
        forecasts = []
        today = datetime.now().date()
        
        for item in data['list']:

            forecast_time = datetime.fromtimestamp(item['dt'])

            if 11 <= forecast_time.hour <= 13:
                forecasts.append({
                    'date': forecast_time.date(),
                    'temp': item['main']['temp'],
                    'weather': item['weather'][0]['description'].capitalize(),
                    'day_name': get_day_name(forecast_time.date())
                })
        
        # Формируем ответ (первые 5 дней, включая сегодня)
        reply = f"📅 Прогноз на 5 дней для {city} ({temp_unit}):\n\n"
        
        for i, forecast in enumerate(forecasts[:5]):
            reply += f"{forecast['day_name']}:\n"
            reply += f"  {forecast['weather']}, {forecast['temp']}{temp_unit}\n\n"
        
        bot.reply_to(message, reply)
    else:
        bot.reply_to(message, f"Не удалось получить прогноз для {city}")

# Вспомогательная функция для названий дней
def get_day_name(date_obj):
    today = datetime.now().date()
    
    if date_obj == today:
        return "Сегодня"
    elif date_obj == today + timedelta(days=1):
        return "Завтра"
    elif date_obj == today + timedelta(days=2):
        return "Послезавтра"
    else:
        # Для остальных дней: Пн, Вт и т.д.
        days_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
        return days_ru[date_obj.weekday()]

# Кнопка "🌤️ Погода сейчас" - вызывает команду /pogoda
@bot.message_handler(func=lambda message: message.text == '🌤️ Погода сейчас')
def button_pogoda(message):
    # Просто вызываем существующую функцию show_weather
    show_weather(message)

# Кнопка "📅 Прогноз на 5 дней" - вызывает команду /forecast
@bot.message_handler(func=lambda message: message.text == '📅 Прогноз на 5 дней')
def button_forecast(message):
    show_forecast(message)

# Кнопка "🏙️ Мой город" - вызывает команду /mycity
@bot.message_handler(func=lambda message: message.text == '🏙️ Мой город')
def button_mycity(message):
    show_city(message)

# Кнопка "⚙️ Настройки" - показывает меню настроек
@bot.message_handler(func=lambda message: message.text == '⚙️ Настройки')
def button_settings(message):
    bot.send_message(
        message.chat.id,
        "⚙️ Настройки:",
        reply_markup=get_settings_keyboard()
    )

# Кнопка "📋 Справка" - вызывает команду /help
@bot.message_handler(func=lambda message: message.text == '📋 Справка')
def button_help(message):
    help_command(message)

# Кнопка "✏️ Изменить город" - показывает подсказку
@bot.message_handler(func=lambda message: message.text == '✏️ Изменить город')
def button_change_city(message):
    user_id = message.from_user.id
    if user_id in user_cities:
        current_city = user_cities[user_id]
        bot.send_message(
            message.chat.id,
            f"Твой текущий город: {current_city}\n\n"
            "Чтобы изменить город, напиши:\n"
            f"/changecity [новый город]\n"
            f"Пример: /changecity Казань",
            reply_markup=get_settings_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id,
            "У тебя еще нет установленного города.\n"
            "Напиши /setcity Москва",
            reply_markup=get_settings_keyboard()
        )

# Кнопка "🌡️ Единицы измерения" - вызывает команду /units
@bot.message_handler(func=lambda message: message.text == '🌡️ Единицы измерения')
def button_units(message):
    change_units(message)
    # После смены показываем клавиатуру настроек снова
    bot.send_message(
        message.chat.id,
        "Выбери действие:",
        reply_markup=get_settings_keyboard()
    )

# Кнопка "⬅️ Назад" - возвращает в главное меню
@bot.message_handler(func=lambda message: message.text == '⬅️ Назад')
def button_back(message):
    bot.send_message(
        message.chat.id,
        "Главное меню:",
        reply_markup=get_main_keyboard()
    )

# Также нужно обновить команду /help чтобы показывала главную клавиатуру
@bot.message_handler(commands=['help'])
def help_command(message):
    user_id = message.from_user.id
    units = user_units.get(user_id, 'C')
    unit_symbol = '°C' if units == 'C' else '°F'
    
    help_text = (
        f"📋 Доступные команды (единицы: {unit_symbol}):\n\n"
        "Текстовые команды:\n"
        "/setcity [город] - установить город\n"
        "/changecity [город] - сменить город\n"
        "\nИли используй кнопки:\n"
        "🌤️ Погода сейчас - текущая погода\n"
        "📅 Прогноз на 5 дней - прогноз\n"
        "🏙️ Мой город - активный город\n"
        "⚙️ Настройки - дополнительные опции"
    )
    bot.send_message(
        message.chat.id,
        help_text,
        reply_markup=get_main_keyboard()
    )

# Запуск
if __name__ == '__main__':
    print("Бот запущен!")
    bot.polling()
