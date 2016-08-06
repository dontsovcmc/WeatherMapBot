# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'


import sys
import os
from logger import log
from datetime import datetime, timedelta

from telegram.ext import Updater
from telegram.ext import CommandHandler, RegexHandler
from telegram.ext import MessageHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton

from service import exception_info

from core import get_continent_name_id, get_region_name_id
from core import get_map_id, get_map_type_id, filter_region_name, filter_type_name
from core import get_map, get_region_by_location, get_region_type_by_map_id
from core import get_legend, get_previous_timestamp_by_path, get_next_timestamp_by_path

from storage import Shelve

from report import report

if 'BOT_TOKEN' in os.environ:
    updater = Updater(token=os.environ['BOT_TOKEN'])
else:
    updater = Updater(token=sys.argv[1])

USER = 'user_id'
MAPTYPE = 'maptype_id'
CONTINENT = 'cont_id'
REGION = 'region_id'
MAPID = 'map_id'

PREVIOUS_MAP = u'<<'
NEXT_MAP = u'>>'
BACK = u'Назад'
MENU = u'Меню'
REFRESH = u'Обновить'

STATE_MENU, STATE_CONT, STATE_REGION, STATE_TYPE, STATE_MAP, SHOW_MAP, STATE_LOCATION = range(7)


show_map_reply_markup = [[KeyboardButton(PREVIOUS_MAP), KeyboardButton(REFRESH), KeyboardButton(NEXT_MAP)],
                            [KeyboardButton(BACK), KeyboardButton(MENU)]]

'''
3.  в отчет - словами
4.  БД типов карт
5.  https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/conversationbot.py
7.  подписка на обновления
8.  request_location
9.  UTC везде
'''

def outside_handler(bot, update):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    bot.sendMessage(update.message.chat_id,
                    text=u'Нажмите /start чтобы начать работу')


def start_handler(bot, update):

    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    reply_keyboard = [[KeyboardButton(u'Отправить местоположение', request_location=True),
                      KeyboardButton(u'Выбрать карту')]]

    # Кнопка предыдущей карты
    with Shelve() as sh:
        map_id = sh.get(chat_id, MAPID)
        if map_id:
            region, mtype = get_region_type_by_map_id(map_id)
            reply_keyboard.append([KeyboardButton(u'%s %s' % (region, mtype))])

    bot.sendMessage(update.message.chat_id,
                    text=u'Добрый день! Я могу отображать карты погоды'
                         u' с различных сайтов. Пришлите мне свое местоположение'
                         u' или выберите карту вручную!',
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
    return STATE_CONT


def command_location_handler(bot, update):

    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    reply_keyboard = [[KeyboardButton(MENU)]]
    bot.sendMessage(chat_id,
                text=u'Чтобы узнать погоду по координатам введите: <широта>,<долгота>',
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
    report.track_screen(user_id, 'location')
    return STATE_LOCATION


def manual_location_handler(bot, update):

    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    text = update.message.text

    try:
        if text == MENU:
            return start_handler(bot, update)

        latidude, longitude = text.split(',')

        region_id = get_region_by_location(float(latidude), float(longitude))
        if not region_id:
            bot.sendMessage(chat_id,
                    text=u'Извините, у меня нет такой карты')
            report.track_screen(user_id, 'location/not_found')
            return STATE_LOCATION

        report.track_screen(user_id, 'location/region/%s' % str(region_id))

        update.message.text = get_region_name_id()[region_id-1][0]
        return region_handler(bot, update)

    except Exception, err:
        return command_location_handler(bot, update)


def location(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    latidude = update.message.location['latitude']
    longitude = update.message.location['longitude']

    region_id = get_region_by_location(latidude, longitude)
    report.track_screen(user_id, 'location/region/%s' % str(region_id))

    update.message.text = get_region_name_id()[region_id-1][0]
    return region_handler(bot, update)


def select_continent(bot, update):

    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    text = update.message.text

    if text == BACK or text == '/manual' or text == u'Выбрать карту':

        reply_keyboard = [[KeyboardButton(d[0])] for d in get_continent_name_id()]
        reply_keyboard.append([KeyboardButton(BACK), KeyboardButton(MENU)])

        bot.sendMessage(chat_id,
                    text=u'Выберите континент',
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))
        report.track_screen(user_id, 'select_continent')
        return STATE_REGION
    else:
        # Предыдущая карта
        return refresh_handler(bot, update)

    return STATE_MENU


def continent_handler(bot, update):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    text = update.message.text

    if text == BACK:
        with Shelve() as sh:
            cont_id = sh.get(chat_id, CONTINENT)
    else:
        found = [cont for cont in get_continent_name_id() if cont[0] == text]
        if not found:
            return STATE_MENU

        cont_id = found[0][1]
        with Shelve() as sh:
            sh.set(chat_id, CONTINENT, cont_id)

    reply_keyboard = [[KeyboardButton(d)] for d in filter_region_name(cont_id)]
    reply_keyboard.append([KeyboardButton(BACK), KeyboardButton(MENU)])

    bot.sendMessage(chat_id,
                text=u'Выберите регион',
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))

    report.track_screen(user_id, 'continent/%s' % str(cont_id))
    return STATE_TYPE



def region_handler(bot, update):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    text = update.message.text

    if text == BACK:
        with Shelve() as sh:
            region_id = sh.get(chat_id, REGION)
            sh.set(chat_id, 'last_map', '')
    else:
        found = [cont for cont in get_region_name_id() if cont[0] == text]
        if not found:
            return STATE_MENU
        region_id = found[0][1]
        with Shelve() as sh:
            sh.set(chat_id, REGION, region_id)
            sh.set(chat_id, 'last_map', '')

    reply_keyboard = [[KeyboardButton(d)] for d in filter_type_name(region_id)]
    reply_keyboard.append([KeyboardButton(BACK), KeyboardButton(MENU)])

    bot.sendMessage(chat_id,
                text=u'Выберите тип',
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))

    report.track_screen(user_id, 'region/%s' % str(region_id))
    return STATE_MAP


def type_handler(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    text = update.message.text

    try:
        found = [cont for cont in get_map_type_id() if cont[0] == text]
        if not found:
            return STATE_MENU

        type_id = found[0][1]
        with Shelve() as sh:
            sh.set(chat_id, MAPTYPE, type_id)

        timestamp = datetime.utcnow()

        with Shelve() as sh:
            sh.set(chat_id, MAPTYPE, type_id)

            map_id = get_map_id(sh.get(chat_id, REGION), type_id)
            sh.set(chat_id, MAPID, map_id)

        report.track_screen(user_id, 'type/%s' % str(type_id))
        return send_map(bot, update, map_id, timestamp)

    except Exception, err:
        bot.sendMessage(chat_id, text=u"Что-то пошло не так. Начать сначала: /start")
    return STATE_MENU


def refresh_handler(bot, update):
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    timestamp = datetime.utcnow()

    with Shelve() as sh:
        map_id = sh.get(chat_id, MAPID)
        report.track_screen(user_id, 'refresh')
        return send_map(bot, update, map_id, timestamp)

    return STATE_MAP


def send_map(bot, update, map_id, timestamp):

    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    path, info = get_map(map_id, timestamp)
    log.info('path %s' % path)

    reply_keyboard = [[KeyboardButton(PREVIOUS_MAP), KeyboardButton(REFRESH), KeyboardButton(NEXT_MAP)],
                      [KeyboardButton(BACK), KeyboardButton(MENU)]]

    with Shelve() as sh:
        last_path = sh.get(chat_id, 'last_map')

        if path and last_path == path:
            bot.sendMessage(chat_id,
                            text=u'<обновление отсутствует>',
                            reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True))

            report.track_screen(user_id, 'map/%s/no_update' % (map_id))
        else:

            if path:
                with open(path.encode('utf-8'), 'rb') as image:
                    bot.sendPhoto(chat_id, image, caption=info.encode('utf-8'),
                                  reply_markup=ReplyKeyboardMarkup(show_map_reply_markup, resize_keyboard=True))

                    report.track_screen(user_id, 'map/%s' % str(map_id))
                    sh.set(chat_id, 'last_map', path)
            else:
                bot.sendMessage(chat_id, text=info + u'\n<изображение отсутствует>',
                                reply_markup=ReplyKeyboardMarkup(show_map_reply_markup, resize_keyboard=True))
                report.track_screen(user_id, 'map/%s/no_image' % str(map_id))
    return SHOW_MAP


def previous_handler(bot, update):

    chat_id = update.message.chat_id
    report.track_screen(update.message.from_user.id, 'previous')

    with Shelve() as sh:
        p = sh.get(chat_id, 'last_map')
        map_id = sh.get(chat_id, MAPID)

    timestamp = get_previous_timestamp_by_path(p)
    return send_map(bot, update, map_id, timestamp)


def next_handler(bot, update):

    chat_id = update.message.chat_id
    report.track_screen(update.message.from_user.id, 'next')

    with Shelve() as sh:
        p = sh.get(chat_id, 'last_map')
        map_id = sh.get(chat_id, MAPID)

    timestamp = get_next_timestamp_by_path(p)
    return send_map(bot, update, map_id, timestamp)


def legend_handler(bot, update):
    chat_id = update.message.chat_id

    with Shelve() as sh:
        map_id = sh.get(chat_id, MAPID)
        if map_id:
            info = get_legend(map_id)
            bot.sendMessage(chat_id, text=info,
                            reply_markup=ReplyKeyboardMarkup(show_map_reply_markup, resize_keyboard=True))
            report.track_screen(update.message.from_user.id, 'legend/%s' % str(map_id))
            return SHOW_MAP

    return STATE_MENU


def error_handler(bot, update, error):

    if update:
        user_id = update.message.from_user.id
        report.track_screen(user_id, '/handle_error')

    log.error('type_handler error: %s' % str(error))
    log.error(exception_info())


conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start_handler),
                  CommandHandler('location', command_location_handler)],

    states={
        STATE_MENU: [CommandHandler('start', start_handler)],

        STATE_CONT: [CommandHandler('location', command_location_handler),
                     RegexHandler('^(Меню)$', start_handler),
                     MessageHandler([Filters.location], location),
                     MessageHandler([Filters.text], select_continent)],

        STATE_REGION: [RegexHandler('^(Назад)$', start_handler),
                    RegexHandler('^(Меню)$', start_handler),
                    MessageHandler([Filters.text], continent_handler)],

        STATE_TYPE: [RegexHandler('^(Назад)$', select_continent),
                    RegexHandler('^(Меню)$', start_handler),
                    MessageHandler([Filters.text], region_handler)],

        STATE_MAP:  [RegexHandler('^(Назад)$', continent_handler),
                    RegexHandler('^(Меню)$', start_handler),
                    MessageHandler([Filters.text], type_handler)],

        SHOW_MAP:   [RegexHandler('^(Меню)$', start_handler),
                    RegexHandler('^(Назад)$', region_handler),
                    RegexHandler('^(Обновить)$', refresh_handler),
                    RegexHandler('^(<<)$', previous_handler),
                    RegexHandler('^(>>)$', next_handler),
                    CommandHandler('legend', legend_handler)],

        STATE_LOCATION: [MessageHandler([Filters.text], manual_location_handler)]
    },

    fallbacks=[CommandHandler('exit', error_handler)]
)


updater.dispatcher.add_handler(conv_handler)
updater.dispatcher.add_handler(MessageHandler([Filters.text], outside_handler))
updater.dispatcher.add_error_handler(error_handler)


from test import test_handler
updater.dispatcher.add_handler(CommandHandler('test', test_handler))

