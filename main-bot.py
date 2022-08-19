import telebot

def telegram_bot(token):
    bot = telebot.TeleBot(token)
    @bot.message_handler(commands=['start'])
    def start_message(message):
        command = f"Цены токенов /price \n" \
                  f"Аналитика продаж /sellstat"
        bot.send_message(message.chat.id, command)

    @bot.message_handler(content_types=['text'])
    def send_text(message):
        if message.text.lower() == '/price':
            try:
                answer = 'привет привет'
                bot.send_message(message.chat.id, answer)
            except Exception as ex:
                print(ex)
                bot.send_message(
                    message.chat.id,
                    "wrong"
                )
        else:
            bot.send_message(
                message.chat.id,
                "Неправильная команда - again"
            )
    bot.polling()
