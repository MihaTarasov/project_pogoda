import telebot

TOKEN = '8599848575:AAF0aUSBXMDKZbJg189Ve7Se-jKtW6BFNrI'

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def send_hello(message):
    bot.reply_to(message, 'Привет, я твой телеграм бот! Пока я ничего не умею, но скоро у меня появится функционал. ')

if __name__ == '__main__':
    print('Бот запущен!')
    bot.polling(none_stop=True)