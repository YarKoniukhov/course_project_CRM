from app import db, Users
from config import TOKEN
import telebot

bot = telebot.TeleBot(TOKEN)


def save_user(msg):
    # Этот код надо для проверки существует ли такой чат уже в базе!
    # people_id = msg.chat.id
    # search_id = Users.query.filter_by(chat_id=people_id).first()
    # if search_id is None:
    user_add = Users(user_name=msg.from_user.first_name, chat_id=msg.chat.id, message=msg.text)
    db.session.add(user_add)
    db.session.flush()
    db.session.commit()
    bot.reply_to(msg, f'Мы с Вами свяжемся!')


@bot.message_handler(commands=['order'])
def order_message(msg):
    bot.reply_to(msg, f'Для оформления заявки - введите сообщение')
    bot.register_next_step_handler(msg, save_user)


@bot.message_handler(commands=['start'])
def send_welcome(msg):
    bot.reply_to(msg, f'Я AdvanceBot. Приятно познакомиться, {msg.from_user.first_name}')


@bot.message_handler(content_types=['text'])
def all_messages(msg):
    message = msg.text
    user_id = msg.chat.id
    bot.send_message(user_id, f"Вы написали: {message}")


bot.polling()