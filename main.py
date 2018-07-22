import config
import telebot
from telebot import types
import json, requests, datetime, re, os, logging
from emoji import emojize
import pymongo

logging.basicConfig(filename='urobobot.log', level = logging.INFO)
conn = pymongo.MongoClient()
db = conn.urobotics
bot = telebot.TeleBot(os.environ['UROBO_TOKEN'])
RECEIVE_ID = os.environ['UROBO_ADMIN_ID']

def saveUsersDB(item):
    collect = db.users
    item.update({'date': datetime.datetime.utcnow()})
    if not bool(collect.find_one({'id': item['id']})):
        collect.insert(item)


def addNumberDB(user_id, number):
    collect = db.users
    msg = bot.send_message(RECEIVE_ID, emojize('Number: ' + number + '\nFrom ' + str(user_id)))
    try:
        collect.update({'id': user_id}, {'number': number})
        return 'Спасибо за заявку! Наш менеджер свяжется с вами в ближайшее время'
    except Exception as e:
        logging.error(e)
        return ('Error! {}'.format(e))

def addEmailDB(user_id, email):
    collect = db.users
    msg = bot.send_message(RECEIVE_ID, emojize('E-mail: ' + email + '\nFrom ' + str(user_id)))
    try:
        collect.update({'id': user_id}, {'email': email})
        return 'Спасибо за заявку! Наш менеджер свяжется с вами в ближайшее время'
    except Exception as e:
        logging.error(e)
        return ('Error! {}'.format(e))


@bot.message_handler(commands=['start'])
def handler_start(message):
    saveUsersDB(message.json['from'])
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    keyboard.add(*[types.KeyboardButton(name) for name in [emojize(':telephone: Свяжитесь со мной'), emojize(':money_with_wings: Попробовать бесплатно'), emojize(':scroll: Условия'),  emojize(':handshake: Для партнеров')]])
    hello_text = 'Привет, {}!\n\n:money_bag: Занимаешься торговлей на криптовалютных биржах?\n:heavy_check_mark: United Robotics поможет автоматизировать твою работу!\n\nЗаказывая проект у нас ты получаешь полное сопровождение бота, начиная от составления технического задания, заканчивая размещением бота.\n\n:label: Работаем в открытую, в двустороннем соглашении\n:shield: Гарантируем безопасность и всегда выполняем свою работу в срок!\nИначе, мы платим штраф! :winking_face:'.format(message.json['from']['first_name'])
    bot.send_message(message.chat.id, emojize(hello_text), reply_markup=keyboard)


@bot.message_handler(content_types=["text"])
def repeat_all_messages(message):
    if message.text[2:] == 'Свяжитесь со мной':
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Ввести номер телефона", callback_data = 'input_phone'))
        keyboard.add(types.InlineKeyboardButton(text="Ввести E-mail", callback_data = 'input_email'))
        keyboard.add(types.InlineKeyboardButton(text="Напишите в Telegram", callback_data = 'connect_telegram'))
        description_text = 'Выбери один из способов связи и укажи контактные данные!\nИ наши менеджеры свяжутся с тобой. :winking_face:'
        bot.send_message(message.chat.id, emojize(description_text), reply_markup=keyboard)
    if message.text[2:] == 'Попробовать бесплатно':
        keyboard = types.InlineKeyboardMarkup()
        for name in ['Торговые индикаторы', 'Мой портфель']:
            keyboard.add(types.InlineKeyboardButton(text=name, callback_data=name))
        description_text = 'Мы подготовили для тебя пару примеров разной тематики,\nкоторые позволяют ознакомиться с простейшими возможностями торговых роботов! :robot_face:\n'
        bot.send_message(message.chat.id, emojize(description_text), reply_markup=keyboard)
    if message.text[2:] == 'Условия':
        description_text = 'С условиями нашей работы можно ознакомиться по ссылке:\n'
        bot.send_message(message.chat.id, emojize(description_text))
    if message.text[2:] == 'Для партнеров':
        description_text = 'Мы приглашаем к сотрудничеству всех желающих!\nИ готовы платить за каждого приведенного клиента 5-10%\nПо вопросам: @webmasta\nТвоя реферальная ссылка: https://t.me/urobotics_bot?start={}'.format(message.chat.id)
        bot.send_message(message.chat.id, emojize(description_text))

def addNumber(message):
    number = message.text
    if number.isdigit:
        tmp = addNumberDB(message.json['from']['id'], number)
        msg = bot.send_message(message.chat.id, tmp)
    else:
        msg = bot.send_message(c.message.chat.id, emojize('Некорректный номер!\nПопробуй еще раз'))
        bot.register_next_step_handler(msg, addNumber)

def addEmail(message):
    email = message.text
    if re.match("[^@]+@[^@]+\.[^@]+", email):
        tmp = addEmailDB(message.json['from']['id'], email)
        msg = bot.send_message(message.chat.id, tmp)
    else:
        msg = bot.send_message(message.chat.id, emojize('Некорректный E-mail!\nПопробуй еще раз'))
        bot.register_next_step_handler(msg, addNumber)

@bot.callback_query_handler(func=lambda c: True)
def inline(c):
    if c.data == 'save_phone':
        bot.register_next_step_handler(c.message.contact, addNumber)
    if c.data == 'input_phone':
        msg = bot.send_message(c.message.chat.id, emojize('Введи номер телефона в формате 79997777777'))
        bot.register_next_step_handler(msg, addNumber)
    if c.data == 'input_email':
        msg = bot.send_message(c.message.chat.id, emojize('Введи свой E-mail в формате my@email.com'))
        bot.register_next_step_handler(msg, addEmail)
    if c.data == 'connect_telegram':
        msg = bot.send_message(RECEIVE_ID, 'Связаться в Телеграм!\nUsername: {}'.format(c.message.json['from']['username']))
        msg = bot.send_message(c.message.chat.id, emojize('Спасибо за заявку! Наш менеджер ответит в ближайшее время'))
    if c.data == 'Торговые индикаторы':
        pass
    if c.data == 'Мой портфель':
        pass

if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logging.error(e)
