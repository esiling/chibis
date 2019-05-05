from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
import requests
import os, os.path
import glob, random
import re

PROXY = {'proxy_url': 'socks5://t1.learn.python.ru:1080', 'urllib3_proxy_kwargs': {'username': 'learn', 'password': 'python'}}


import logging
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log'
                    )

def main():
    with open('key.txt') as f:
        key = f.read()
    mybot = Updater(key, request_kwargs=PROXY)
    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user, pass_user_data=True))
    dp.add_handler(CommandHandler("help", help_user, pass_user_data=True))
    dp.add_handler(CommandHandler("info", info_user, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.text, birdname, pass_user_data=True))
    dp.add_handler(MessageHandler(Filters.voice, receiveMessage, pass_user_data=True))
    #dp.add_handler(MessageHandler(Filters.voice, trueMessage, pass_user_data=True))
    #dp.add_handler(MessageHandler(Filters.all, countme))
    mybot.start_polling()
    mybot.idle()

latin_names = {'зяблик': 'Fringilla-coelebs', 'fringilla coelebs': 'Fringilla-coelebs','большая синица': 'Parus-major', 'синица большая': 'Parus-major', 'parus major': 'Parus-major', 'лазоревка': 'Cyanistes-caeruleus', 'cyanistes caeruleus': 'Cyanistes-caeruleus', 
    'пухляк': 'Poecile-montanus', 'poecile montanus': 'Poecile-montanus', 'полевой жаворонок': 'Alauda-arvensis', 'alauda arvensis': 'Alauda-arvensis', 'луговой чекан': 'Saxicola-rubetra', 'saxicola rubetra': 'Saxicola-rubetra', 
    'каменка': 'Oenanthe-oenanthe', 'oenanthe oenanthe': 'Oenanthe-oenanthe', 'варакушка': 'Luscinia-svecica', 'luscinia svecica': 'Luscinia-svecica', 'чечевица': 'Carpodacus-erythrinus', 'carpodacus erythrinus': 'Carpodacus-erythrinus', 
    'сорока': 'Pica-pica', 'pica pica': 'Pica-pica', 'сойка': 'Garrulus-glandarius', 'garrulus glandarius': 'Garrulus-glandarius', 'серая ворона': 'Corvus-cornix', 'corvus cornix': 'Corvus-cornix', 'ворон': 'Corvus-corax', 'corvus corax': 'Corvus-corax', 
    'чибис': 'Vanellus-vanellus', 'vanellus vanellus': 'Vanellus-vanellus', 'кряква': 'Anas-platyrhynchos', 'anas platyrhynchos': 'Anas-platyrhynchos', 'чайка озерная': 'Chroicocephalus-ridibundus', 'озерная чайка': 'Chroicocephalus-ridibundus', 'chroicocephalus ridibundus': 'Chroicocephalus-ridibundus', 
    'зеленушка': 'Chloris-chloris', 'chloris chloris': 'Chloris-chloris', 'дрозд белобровик': 'Turdus-iliacus', 'turdus iliacus': 'Turdus-iliacus', 'дрозд рябинник': 'Turdus-pilaris', 'turdus pilaris': 'Turdus-pilaris', 
    'дрозд черный': 'Turdus-merula', 'turdus merula': 'Turdus-merula', 'скворец': 'Sturnus-vulgaris', 'sturnus vulgaris': 'Sturnus-vulgaris', 'зарянка': 'Erithacus-rubecula', 'erithacus rubecula': 'Erithacus-rubecula', 
    'снегирь': 'Pyrrhula-pyrrhula', 'pyrrhula pyrrhula': 'Pyrrhula-pyrrhula', 'поползень': 'Sitta-europaea', 'sitta europaea': 'Sitta-europaea'}

def greet_user(bot, update, user_data):
    print('Вызван /start')
    update.message.reply_text('Здравствуйте, любитель птичек! На связи Шазам для птиц. Чтобы узнать обо мне, выберите /help. Ползуйтесь /info для получения списка птиц, которых я знаю. Я помогу вам определить птиц Подмосковья по их голосу. Запишите голосовое сообщение с пением птицы, и я помогу вам определить ее вид. Отправьте мне русское или латинское название птицы, и я пришлю запись ее пения.')


def birdname(bot, update, user_data):
    try:    
        print('I am here')
        user_text = update.message.text.lower()
        if user_text in latin_names:
            species_name = latin_names[user_text]
            filename = random.choice(glob.glob('subset/'+species_name + '-*.mp3'))
            update.message.reply_audio(open(filename,'rb'))
            update.message.reply_text('https://ru.wikipedia.org/wiki/' + re.sub('-', '_', species_name))
        else:
            update.message.reply_text('Все птички - зяблики, все травки - мятлики! Такой птицы я не знаю, но, возможно, это зяблик. Попробуйте /help')
    except Exception as e:
        print(e)

def receiveMessage(bot, update, user_data):
    try:
        # update.message.reply_text("Обрабатываю данные")
        os.makedirs('downloads', exist_ok=True)
        print(update)
        voice_file = bot.get_file(update.message.voice.file_id)
        filename = os.path.join('downloads', '{}.mp3'.format(voice_file.file_id))
        voice_file.download(filename)
        species_name = random.choice(list(set(latin_names.values())))
        # update.message.reply_text()
        update.message.reply_text('https://ru.wikipedia.org/wiki/' + re.sub('-', '_', species_name))
        # update.message.reply_text("Файл сохранен")
    except Exception as e:
        print(e)
    #user_voice = update.message.voice
    #print(user_voice)
    #update.message.reply_voice(user_voice)

def help_user(bot, update, user_data):
    print('Запрошена помощь /help')
    update.message.reply_text('На связи Шазам для птиц! Я помогу вам определить птиц Подмосковья по их голосу. Запишите голосовое сообщение с пением птицы, и я помогу вам определить ее вид. Отправьте мне русское или латинское название птицы, и я пришлю запись ее пения.')

def info_user(bot, update, user_data):
    print('Информация /info')
    update.message.reply_text('Птицы, которых я знаю:\nЗяблик  (Fringilla coelebs)\nБольшая синица  (Parus major)\nЛазоревка   Cyanistes caeruleus)\nПухляк  (Poecile montanus)\nПолевой жаворонок   (Alauda arvensis)\nЛуговой чекан   (Saxicola rubetra)\nКаменка Oenanthe (oenanthe)\nВаракушка   (Luscinia svecica)\nЧечевица    (Carpodacus erythrinus)\nСорока  (Pica pica)\nСойка   (Garrulus glandarius)\nСерая ворона    (Corvus cornix)\nВорон   (Corvus corax)\nКряква  (Anas platyrhynchos)\nЧайка озерная   (Chroicocephalus ridibundus)\nЗеленушка   (Chloris chloris)\nДрозд белобровик    (Turdus iliacus)\nДрозд рябинник  (Turdus pilaris)\nДрозд черный    (Turdus merula)\nСкворец (Sturnus vulgaris)\nЗарянка (Erithacus rubecula)\nСнегирь (Pyrrhula pyrrhula)\nПоползень   (Sitta europaea)\n')

#def trueMessage(bot, update, user_data):
    #print(Получил голосовое сообщение)
    #update.message.reply_text('Похоже, это' +)
#или:
#@bot.message_handler(content_types=['voice'])
#def voice_processing(message):
    #file_info = bot.get_file(message.voice.file_id)
    #file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(789454327:AAGs4Kzt53E142DzAqJg8-A6rb6kZOrQvXg, file_info.file_path)) 

#def countme(bot, update):


if __name__=="__main__":
    main()
    #









