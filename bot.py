from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ReplyKeyboardMarkup
import requests
import os, os.path
import glob, random
import re
import librosa

import json
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, matthews_corrcoef, confusion_matrix
from sklearn.metrics import make_scorer

from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import GridSearchCV, cross_val_score

import logging
logging.basicConfig(format='%(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='bot.log')

PROXY = {'proxy_url': 'socks5://t1.learn.python.ru:1080', 'urllib3_proxy_kwargs': {'username': 'learn', 'password': 'python'}}


def precalculate_optimal_model_params():
    features = pd.read_csv('mean_mels.tsv', index_col=0, sep='\t')
    audio_filenames = features.index.tolist()
    species_labels = [str(x).split('.')[0].split('-')[0]+'_' +str(x).split('.')[0].split('-')[1] for x in audio_filenames]
    features['label'] = species_labels
    unlabelled_dataset = features.drop('label', axis=1)
    species_types = set(species_labels)
    for bird in species_types:
        if not os.path.exists(f'models/knn/{bird}.json'):
            labels = np.where(features['label'] == bird, 1, 0)
            unlabelled_dataset = features.drop('label', axis=1)
            model = KNeighborsClassifier()
            params = {'n_neighbors': [1,3,5,7, 10, 15], 
                  'weights':['uniform', 'distance'],
                  'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute']}
            grid_searcher = GridSearchCV(model, params, cv=3, n_jobs=12, verbose=True, scoring = 'precision', refit='precision')
            grid_searcher.fit(unlabelled_dataset, labels)
            with open(f'models/knn/{bird}.json', 'w+') as fw:
                json.dump({'params': grid_searcher.best_params_, 'score': grid_searcher.best_score_}, fw)

def load_models():
    features = pd.read_csv('mean_mels.tsv', index_col=0, sep='\t')
    audio_filenames = features.index.tolist()
    species_labels = [str(x).split('.')[0].split('-')[0]+'_' +str(x).split('.')[0].split('-')[1] for x in audio_filenames]
    features['label'] = species_labels
    unlabelled_dataset = features.drop('label', axis=1)
    species_types = set(species_labels)

    models = {}
    for bird in species_types:
        labels = np.where(features['label'] == bird, 1, 0)
        with open(f'models/knn/{bird}.json') as fw:
            model_infos = json.load(fw)
        params = model_infos['params']
        model = KNeighborsClassifier(**params)
        model.fit(unlabelled_dataset, labels)
        models[bird] = model
    return models

def get_predictions(models, filename):
    x, fs = librosa.load(filename)
    spec = librosa.feature.melspectrogram(x, sr=fs, n_mels=128)
    spec_mean = np.mean(spec, axis=1)
    predictions = {}
    for bird, model in models.items():
        # 0-th sample, 1-st class - bird found (vs 0-th class "bird not found")
        prob = model.predict_proba(spec_mean.reshape(1, -1))[0][1]
        predictions[bird] = prob
    return predictions



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
    dp.add_handler(MessageHandler(Filters.audio, receiveMessage, pass_user_data=True))
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

def wiki_link(species_name):
    return 'https://ru.wikipedia.org/wiki/' + re.sub('-', '_', species_name)

def receiveMessage(bot, update, user_data):
    try:
        # update.message.reply_text("Обрабатываю данные")
        os.makedirs('downloads', exist_ok=True)
        print(update)
        if update.message.voice:
            audio = update.message.voice
        elif update.message.audio:
            audio = update.message.audio
        voice_file = bot.get_file(audio.file_id)
        filename = os.path.join('downloads', '{}.mp3'.format(audio.file_id))
        voice_file.download(filename)
        update.message.reply_text('Файл получен, приступаю к обработке')
        predictions = get_predictions(MODELS, filename)
        predictions = sorted(predictions.items(), key=lambda bird_prob: bird_prob[1], reverse=True)
        predicted_birds = [bird_prob for bird_prob in predictions if bird_prob[1] > 0.5]
        print(predictions)

        if len(predicted_birds) > 0:
            msgs = [f'{wiki_link(bird_prob[0])} с вероятностью {(bird_prob[1] * 100).round()}%' for bird_prob in predicted_birds]
            update.message.reply_text('\n'.join(msgs))
        elif len(predicted_birds) == 0:
            species_name = predictions[0][0]
            update.message.reply_text(f'Не узнаю. Но наиболее вероятно, это {wiki_link(species_name)}')
    except Exception as e:
        print(e)

def help_user(bot, update, user_data):
    print('Запрошена помощь /help')
    update.message.reply_text('На связи Шазам для птиц! Я помогу вам определить птиц Подмосковья по их голосу. Запишите голосовое сообщение с пением птицы, и я помогу вам определить ее вид. Отправьте мне русское или латинское название птицы, и я пришлю запись ее пения.')

def info_user(bot, update, user_data):
    print('Информация /info')
    update.message.reply_text('Птицы, которых я знаю:\nЗяблик  (Fringilla coelebs)\nБольшая синица  (Parus major)\nЛазоревка   Cyanistes caeruleus)\nПухляк  (Poecile montanus)\nПолевой жаворонок   (Alauda arvensis)\nЛуговой чекан   (Saxicola rubetra)\nКаменка Oenanthe (oenanthe)\nВаракушка   (Luscinia svecica)\nЧечевица    (Carpodacus erythrinus)\nСорока  (Pica pica)\nСойка   (Garrulus glandarius)\nСерая ворона    (Corvus cornix)\nВорон   (Corvus corax)\nКряква  (Anas platyrhynchos)\nЧайка озерная   (Chroicocephalus ridibundus)\nЗеленушка   (Chloris chloris)\nДрозд белобровик    (Turdus iliacus)\nДрозд рябинник  (Turdus pilaris)\nДрозд черный    (Turdus merula)\nСкворец (Sturnus vulgaris)\nЗарянка (Erithacus rubecula)\nСнегирь (Pyrrhula pyrrhula)\nПоползень   (Sitta europaea)\n')

if __name__=="__main__":
    precalculate_optimal_model_params()
    MODELS = load_models()
    main()
