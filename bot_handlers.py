from telebot import types
import keyboards
from weather_service import WeatherService


class BotHandlers:
    """Обработчики команд бота"""
    
    def __init__(self, bot, weather_service=None):
        self.bot = bot
        self.weather_service = weather_service or WeatherService()
        self.user_cities = {}
        self.user_units = {}
        
        self._register_handlers()
    
    def _register_handlers(self):
        """Регистрация всех обработчиков"""
        @self.bot.message_handler(commands=['start'])
        def start_wrapper(message):
            self.start(message)
        
        @self.bot.message_handler(commands=['units'])
        def change_units_wrapper(message):
            self.change_units(message)
        
        @self.bot.message_handler(func=lambda m: m.text and m.text.startswith('/setcity'))
        def set_city_wrapper(message):
            self.set_city(message)
        
        @self.bot.message_handler(commands=['pogoda'])
        def show_weather_wrapper(message):
            self.show_weather(message)
        
        @self.bot.message_handler(commands=['mycity'])
        def show_city_wrapper(message):
            self.show_city(message)
        
        @self.bot.message_handler(func=lambda m: m.text and m.text.startswith('/changecity'))
        def change_city_wrapper(message):
            self.change_city(message)
        
        @self.bot.message_handler(commands=['forgetcity'])
        def forget_city_wrapper(message):
            self.forget_city(message)
        
        @self.bot.message_handler(commands=['forecast'])
        def show_forecast_wrapper(message):
            self.show_forecast(message)
        
        @self.bot.message_handler(commands=['help'])
        def help_wrapper(message):
            self.help_command(message)
        
        # Обработчики кнопок
        @self.bot.message_handler(func=lambda message: message.text == '🌤️ Погода сейчас')
        def button_pogoda_wrapper(message):
            self.show_weather(message)
        
        @self.bot.message_handler(func=lambda message: message.text == '📅 Прогноз на 5 дней')
        def button_forecast_wrapper(message):
            self.show_forecast(message)
        
        @self.bot.message_handler(func=lambda message: message.text == '🏙️ Мой город')
        def button_mycity_wrapper(message):
            self.show_city(message)
        
        @self.bot.message_handler(func=lambda message: message.text == '⚙️ Настройки')
        def button_settings_wrapper(message):
            self.bot.send_message(
                message.chat.id,
                "⚙️ Настройки:",
                reply_markup=keyboards.get_settings_keyboard()
            )
        
        @self.bot.message_handler(func=lambda message: message.text == '📋 Справка')
        def button_help_wrapper(message):
            self.help_command(message)
        
        @self.bot.message_handler(func=lambda message: message.text == '✏️ Изменить город')
        def button_change_city_wrapper(message):
            user_id = message.from_user.id
            if user_id in self.user_cities:
                current_city = self.user_cities[user_id]
                self.bot.send_message(
                    message.chat.id,
                    f"Твой текущий город: {current_city}\n\n"
                    "Чтобы изменить город, напиши:\n"
                    f"/changecity [новый город]\n"
                    f"Пример: /changecity Казань",
                    reply_markup=keyboards.get_settings_keyboard()
                )
            else:
                self.bot.send_message(
                    message.chat.id,
                    "У тебя еще нет установленного города.\n"
                    "Напиши /setcity Москва",
                    reply_markup=keyboards.get_settings_keyboard()
                )
        
        @self.bot.message_handler(func=lambda message: message.text == '🌡️ Единицы измерения')
        def button_units_wrapper(message):
            self.change_units(message)
            self.bot.send_message(
                message.chat.id,
                "Выбери действие:",
                reply_markup=keyboards.get_settings_keyboard()
            )
        
        @self.bot.message_handler(func=lambda message: message.text == '⬅️ Назад')
        def button_back_wrapper(message):
            self.bot.send_message(
                message.chat.id,
                "Главное меню:",
                reply_markup=keyboards.get_main_keyboard()
            )
    
    def start(self, message):
        """Обработчик команды /start"""
        user_id = message.from_user.id
        
        units = self.user_units.get(user_id, 'C')
        unit_symbol = '°C' if units == 'C' else '°F'
        
        if user_id in self.user_cities:
            self.bot.send_message(
                message.chat.id,
                f"Привет! Я уже знаю твой город: {self.user_cities[user_id]}\n"
                f"Единицы измерения: {unit_symbol}\n\n"
                f"Используй кнопки ниже или команды:",
                reply_markup=keyboards.get_main_keyboard()
            )
        else:
            self.bot.send_message(
                message.chat.id,
                "Привет! Я бот для погоды. Сначала установи свой город:\n"
                "Напиши /setcity и название города\n"
                f"Единицы измерения: {unit_symbol}\n"
                "Например: /setcity Москва",
                reply_markup=keyboards.get_main_keyboard()
            )
    
    def change_units(self, message):
        """Обработчик команды /units"""
        user_id = message.from_user.id
        current_units = self.user_units.get(user_id, 'C')
        
        if current_units == 'C':
            self.user_units[user_id] = 'F'
            new_units = '°F (Фаренгейт)'
            old_units = '°C (Цельсий)'
        else:
            self.user_units[user_id] = 'C'
            new_units = '°C (Цельсий)'
            old_units = '°F (Фаренгейт)'
        
        self.bot.reply_to(message, 
            f"✅ Единицы измерения изменены:\n"
            f"Было: {old_units}\n"
            f"Стало: {new_units}\n\n"
            f"Теперь погода будет показываться в {new_units}")
    
    def set_city(self, message):
        """Обработчик команды /setcity"""
        user_id = message.from_user.id
        text = message.text.strip()
        
        if text == '/setcity':
            units = self.user_units.get(user_id, 'C')
            unit_symbol = '°C' if units == 'C' else '°F'
            self.bot.reply_to(message, 
                f"Напиши /setcity и название города\n"
                f"Единицы: {unit_symbol}\n"
                f"Пример: /setcity Москва")
            return
        
        try:
            city = text[9:].strip()
            
            if not city:
                self.bot.reply_to(message, "Укажи город! Пример: /setcity Москва")
                return
            
            # Проверяем город через API
            data = self.weather_service.get_current_weather(city)
            
            if data.get('cod') == 200:
                self.user_cities[user_id] = city
                units = self.user_units.get(user_id, 'C')
                unit_symbol = '°C' if units == 'C' else '°F'
                
                self.bot.reply_to(message, 
                    f"✅ Город установлен: {city}\n"
                    f"Единицы измерения: {unit_symbol}\n"
                    f"Теперь пиши /pogoda для получения погоды!")
            else:
                self.bot.reply_to(message, f"❌ Город '{city}' не найден. Попробуй другой.")
                
        except Exception as e:
            self.bot.reply_to(message, f"Ошибка: {e}")
    
    def show_weather(self, message):
        """Обработчик команды /pogoda"""
        user_id = message.from_user.id
        
        if user_id not in self.user_cities:
            self.bot.reply_to(message, "Сначала установи город командой /setcity")
            return
        
        city = self.user_cities[user_id]
        units = self.user_units.get(user_id, 'C')
        
        try:
            data = self.weather_service.get_current_weather(city, units)
            
            if data.get('cod') == 200:
                weather = data['weather'][0]['description'].capitalize()
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                humidity = data['main']['humidity']
                temp_unit = '°C' if units == 'C' else '°F'
                
                reply = (f"🌤️ Погода в {city} ({temp_unit}):\n"
                        f"• {weather}\n"
                        f"• Температура: {temp}{temp_unit}\n"
                        f"• Ощущается как: {feels_like}{temp_unit}\n"
                        f"• Влажность: {humidity}%")
                
                self.bot.reply_to(message, reply)
        except Exception as e:
            self.bot.reply_to(message, f"Ошибка: {e}")
    
    def show_city(self, message):
        """Обработчик команды /mycity"""
        user_id = message.from_user.id
        
        if user_id in self.user_cities:
            units = self.user_units.get(user_id, 'C')
            unit_symbol = '°C' if units == 'C' else '°F'
            
            self.bot.reply_to(message, 
                f"🏙️ Твой активный город: {self.user_cities[user_id]}\n"
                f"📏 Единицы измерения: {unit_symbol}")
        else:
            self.bot.reply_to(message, 
                "У тебя еще нет установленного города.\n"
                "Напиши /setcity Москва")
    
    def change_city(self, message):
        """Обработчик команды /changecity"""
        user_id = message.from_user.id
        text = message.text.strip()
        
        if text == '/changecity':
            units = self.user_units.get(user_id, 'C')
            unit_symbol = '°C' if units == 'C' else '°F'
            self.bot.reply_to(message, 
                f"Напиши /changecity и новый город\n"
                f"Единицы: {unit_symbol}\n"
                f"Пример: /changecity Санкт-Петербург")
            return
        
        old_city = self.user_cities.get(user_id, "не установлен")
        
        try:
            new_city = text[12:].strip()
            
            if not new_city:
                self.bot.reply_to(message, "Укажи новый город! Пример: /changecity Санкт-Петербург")
                return
            
            data = self.weather_service.get_current_weather(new_city)
            
            if data.get('cod') == 200:
                self.user_cities[user_id] = new_city
                units = self.user_units.get(user_id, 'C')
                unit_symbol = '°C' if units == 'C' else '°F'
                
                self.bot.reply_to(message, 
                    f"✅ Город изменен!\n"
                    f"Старый: {old_city}\n"
                    f"Новый: {new_city}\n"
                    f"Единицы: {unit_symbol}")
            else:
                self.bot.reply_to(message, f"❌ Город '{new_city}' не найден. Попробуй другой.")
                
        except Exception as e:
            self.bot.reply_to(message, f"Ошибка: {e}")
    
    def forget_city(self, message):
        """Обработчик команды /forgetcity"""
        user_id = message.from_user.id
        
        if user_id in self.user_cities:
            removed_city = self.user_cities.pop(user_id)
            self.bot.reply_to(message, 
                f"🗑️ Город '{removed_city}' удален из памяти.\n"
                f"Установи новый город через /setcity")
        else:
            self.bot.reply_to(message, "У тебя нет сохраненного города.")
    
    def show_forecast(self, message):
        """Обработчик команды /forecast"""
        user_id = message.from_user.id
        
        if user_id not in self.user_cities:
            self.bot.reply_to(message, "Сначала установи город командой /setcity")
            return
        
        city = self.user_cities[user_id]
        units = self.user_units.get(user_id, 'C')
        
        try:
            data = self.weather_service.get_forecast(city, units)
            reply = self.weather_service.format_forecast_response(data, city, units)
            
            if reply:
                self.bot.reply_to(message, reply)
            else:
                self.bot.reply_to(message, f"Не удалось получить прогноз для {city}")
        except Exception as e:
            self.bot.reply_to(message, f"Ошибка: {e}")
    
    def help_command(self, message):
        """Обработчик команды /help"""
        user_id = message.from_user.id
        units = self.user_units.get(user_id, 'C')
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
        self.bot.send_message(
            message.chat.id,
            help_text,
            reply_markup=keyboards.get_main_keyboard()
        )