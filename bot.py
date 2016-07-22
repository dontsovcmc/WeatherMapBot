# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import sys
from logger import log


from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters

from telegram import ForceReply, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup

from core import init as db_init
from core import CHANGE_SITE, CHANGE_MAP, REFRESH
from core import maps_keyboard_layout, sites_keyboard_layout, get_site_id, get_sql_map_id
from core import get_map

#import botan

BOT_KEY = sys.argv[1]

updater = Updater(token=BOT_KEY)

MENU, CHOOSE_SITE, CHOOSE_MAP, WATCH_MAP = range(4)

from storage import Shelve

def set_user_data(chat_id, state, user_id=None, site_id=None, map_id=None):
    with Shelve() as sh:
        sh.set(chat_id, 'state', state)
        sh.set(chat_id, 'user_id', user_id)
        sh.set(chat_id, 'site_id', site_id)
        sh.set(chat_id, 'map_id', map_id)



def start(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    text = update.message.text

    try:
        with Shelve() as sh:
            chat_state = sh.get(chat_id, 'state', MENU)
            chat_user = sh.get(chat_id, 'user_id', None)

        if chat_state == MENU or text == '/start':
            set_user_data(chat_id, CHOOSE_SITE, user_id)

            reply_markup = ReplyKeyboardMarkup(sites_keyboard_layout(KeyboardButton), one_time_keyboard=True, resize_keyboard=True)
            bot.sendMessage(chat_id, text="Выберите сайт", reply_markup=reply_markup)

        elif chat_user and chat_user == user_id:

                if update.message.text == CHANGE_SITE:

                    set_user_data(chat_id, MENU, user_id)
                    update.message.text = '/start'
                    start(bot, update)

                elif update.message.text == CHANGE_MAP:

                    with Shelve() as sh:
                        site_id = sh.get(chat_id, 'site_id', '')
                        set_user_data(chat_id, CHOOSE_SITE, user_id, site_id)

                    update.message.text = site_id
                    start(bot, update)

                elif chat_state == CHOOSE_SITE:
                    site_id = get_site_id(update.message.text) # bot_path
                    if site_id:
                        set_user_data(chat_id, CHOOSE_MAP, user_id, site_id)
                        reply_markup = ReplyKeyboardMarkup(maps_keyboard_layout(site_id, KeyboardButton),
                                                           one_time_keyboard=True, resize_keyboard=True)
                        bot.sendMessage(chat_id, text="Выберите карту", reply_markup=reply_markup)

                elif chat_state == CHOOSE_MAP:

                    with Shelve() as sh:
                        site_id = sh.get(chat_id, 'site_id', '')

                    map_id = get_sql_map_id(update.message.text)
                    if map_id:
                        set_user_data(chat_id, WATCH_MAP, user_id, site_id, map_id)

                        reply_markup = ReplyKeyboardMarkup([[KeyboardButton(CHANGE_SITE),
                                                             KeyboardButton(CHANGE_MAP),
                                                             KeyboardButton(REFRESH)]],
                                                            one_time_keyboard=True, resize_keyboard=True)
                        try:
                            path, info = get_map(map_id)
                            log.info('path %s' % path)

                            bot.sendMessage(chat_id, text=info, reply_markup=reply_markup)

                            if path:
                                with open(path, 'rb') as image:
                                    bot.sendPhoto(chat_id, image, reply_markup=reply_markup)
                            else:
                                bot.sendMessage(chat_id, text='<изображение отсутствует>', reply_markup=reply_markup)
                        except Exception, err:
                            bot.sendMessage(chat_id, text='<internal error>', reply_markup=reply_markup)

                elif chat_state == WATCH_MAP:

                    if text == REFRESH:
                        with Shelve() as sh:
                            sh.set(chat_id, 'state', CHOOSE_MAP)
                            update.message.text = sh.get(chat_id, 'map_id', '/start')

                        start(bot, update)

                else:
                    set_user_data(chat_id, MENU, user_id)
                    bot.sendMessage(chat_id,
                                    text="Что-то пошло не так /start")

    except Exception, err:
        set_user_data(chat_id, MENU, user_id)
        update.message.text = '/start'
        start(bot, update)


def test_handler(bot, update):

    from datetime import datetime

    chat_id = update.message.chat_id
    try:
        try:
            reply_markup = ReplyKeyboardMarkup([[KeyboardButton(CHANGE_SITE),
                                                             KeyboardButton(CHANGE_MAP),
                                                             KeyboardButton(REFRESH)]],
                                                            one_time_keyboard=True, resize_keyboard=True)

            map_id = 2
            path, info = get_map(map_id, datetime.now())
            log.info('path %s' % path)

            bot.sendMessage(chat_id, text=info, reply_markup=reply_markup)
            if path:
                with open(path, 'rb') as image:
                    bot.sendPhoto(chat_id, image, reply_markup=reply_markup)
            else:
                bot.sendMessage(chat_id, text='<изображение отсутствует>', reply_markup=reply_markup)

        except Exception, err:
            log.error(err)
            bot.sendMessage(chat_id, text='<internal error>', reply_markup=reply_markup)

    except Exception, err:
        log.error(err)
        bot.sendMessage(chat_id, text='<internal error>', reply_markup=reply_markup)



updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler([Filters.text], start))

updater.dispatcher.add_handler(CommandHandler('test', test_handler))


def main():

    db_init()
    updater.start_polling()

