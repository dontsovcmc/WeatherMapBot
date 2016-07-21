# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import sys
from logger import log


from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters

from telegram import ForceReply, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup

from core import init as db_init
from core import CHANGE_SITE
from core import maps_keyboard_layout, sites_keyboard_layout, get_site_id, get_sql_map_id, get_sql_map
from maps import get_weather_map

#import botan

#BOTAN_KEY = '' #sys.argv[2]
BOT_KEY = sys.argv[1]

updater = Updater(token=BOT_KEY)

MENU, CHOOSE_SITE, CHOOSE_MAP, WATCH_MAP = range(4)

from storage import shelve_get, shelve_set


def start(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    text = update.message.text
    chat_state = shelve_get(chat_id, 'state', MENU)

    chat_user = shelve_get(chat_id, 'user_id', None)

    if chat_state == MENU and text == '/start':
        #botan.track(BOT_KEY, chat_id, 'start')
        #with open(r"D:\af_settings.png", "rb") as f:
        #    bot.sendPhoto(chat_id, f)

        shelve_set(chat_id, 'state', CHOOSE_SITE)
        shelve_set(chat_id, 'user_id', user_id)

        reply_markup = ReplyKeyboardMarkup(sites_keyboard_layout(KeyboardButton), one_time_keyboard=True, resize_keyboard=True)
        bot.sendMessage(chat_id, text="Выберите сайт", reply_markup=reply_markup)

    elif chat_state == CHOOSE_SITE and chat_user and chat_user == user_id:
        #botan.track(BOT_KEY, chat_id, 'CHOOSE_SITE')

        site_id = get_site_id(update.message.text) # bot_path
        if site_id:
            shelve_set(chat_id, 'state', CHOOSE_MAP)
            shelve_set(chat_id, 'site_id', site_id)
            reply_markup = ReplyKeyboardMarkup(maps_keyboard_layout(site_id, KeyboardButton), one_time_keyboard=True, resize_keyboard=True)
            bot.sendMessage(chat_id, text="Выберите карту", reply_markup=reply_markup)
        else:
            shelve_set(chat_id, 'state', CHOOSE_SITE)
            shelve_set(chat_id, 'site_id', '')
            shelve_set(chat_id, 'map_id', '')
            update.message.text = '/start'
            start(bot, update)

    elif chat_state == CHOOSE_MAP and chat_user and chat_user == user_id:

        if update.message.text == CHANGE_SITE:

            shelve_set(chat_id, 'state', MENU)
            shelve_set(chat_id, 'site_id', '')
            shelve_set(chat_id, 'map_id', '')
            update.message.text = '/start'
            start(bot, update)

        else:

            map_id = get_sql_map_id(update.message.text)

            if map_id:
                shelve_set(chat_id, 'state', WATCH_MAP)
                shelve_set(chat_id, 'map_id', map_id)

                reply_markup = ReplyKeyboardMarkup([[KeyboardButton(CHANGE_SITE), KeyboardButton("Выбор карты"), KeyboardButton("Обновить")]],
                                                    one_time_keyboard=True, resize_keyboard=True)
                try:
                    name = get_sql_map(map_id).name
                    wmap = get_weather_map(name)
                    timestamp, path = wmap.now()

                    log.info('path %s' % path)

                    bot.sendMessage(chat_id, text=wmap.map_info(timestamp), reply_markup=reply_markup)

                    if path:
                        with open(path, 'rb') as image:
                            bot.sendPhoto(chat_id, image, reply_markup=reply_markup)
                    else:
                        bot.sendMessage(chat_id, text='<изображение отсутствует>', reply_markup=reply_markup)
                except Exception, err:
                    bot.sendMessage(chat_id, text='<internal error>', reply_markup=reply_markup)

            else:
                shelve_set(chat_id, 'state', CHOOSE_SITE)
                site_id = shelve_get(chat_id, 'site_id', '')
                update.message.text = site_id
                start(bot, update)


    elif chat_state == WATCH_MAP and chat_user and chat_user == user_id:

        if text == CHANGE_SITE:
            shelve_set(chat_id, 'state', MENU)
            shelve_set(chat_id, 'site_id', '')
            shelve_set(chat_id, 'map_id', '')

            update.message.text = '/start'
            start(bot, update)

        elif text == u'Выбор карты':
            shelve_set(chat_id, 'state', CHOOSE_SITE)
            update.message.text = shelve_get(chat_id, 'site_id', '/start')
            start(bot, update)

        elif text == u'Обновить':
            shelve_set(chat_id, 'state', CHOOSE_MAP)
            update.message.text = shelve_get(chat_id, 'map_id', '/start')
            start(bot, update)

        else: # Update
            update.message.text = '/start'
            start(bot, update)
    else:
        shelve_set(chat_id, 'state', MENU)
        shelve_set(chat_id, 'site_id', '')
        shelve_set(chat_id, 'map_id', '')
        bot.sendMessage(chat_id,
                        text="Что-то пошло не так /start")


def test_handler(bot, update):

    from maps.GisMeteoParser import GisMeteoMap
    chat_id = update.message.chat_id
    try:
        wmap = GisMeteoMap(u'МО: Осадки', '569')
        timestamp, path = wmap.now()
        bot.sendMessage(chat_id, text=wmap.map_info(timestamp))

        log.info('path %s' % path)

    except Exception, err:
        bot.sendMessage(chat_id, text=str(err))


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler([Filters.text], start))

updater.dispatcher.add_handler(CommandHandler('test', test_handler))


def main():

    db_init()
    updater.start_polling()

