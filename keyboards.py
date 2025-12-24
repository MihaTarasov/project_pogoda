from telebot import types


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