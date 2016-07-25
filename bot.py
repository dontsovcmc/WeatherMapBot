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
from core import get_map, get_sql_map_name, get_sql_site_bot_path
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound

#import botan

BOT_KEY = sys.argv[1]

updater = Updater(token=BOT_KEY)

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
            chat_user = sh.get(chat_id, 'user_id', None)

        if text == '/start':
            set_user_data(chat_id, '', user_id)

            reply_markup = ReplyKeyboardMarkup(sites_keyboard_layout(KeyboardButton), one_time_keyboard=True, resize_keyboard=True)
            bot.sendMessage(chat_id, text="Выберите сайт", reply_markup=reply_markup)

        elif chat_user and chat_user == user_id:

                if update.message.text == CHANGE_SITE:

                    set_user_data(chat_id, '', user_id, '', '')
                    update.message.text = '/start'
                    start(bot, update)

                elif update.message.text == CHANGE_MAP:

                    with Shelve() as sh:
                        sh.set(chat_id, 'map_id', '')
                        update.message.text = get_sql_site_bot_path(sh.get(chat_id, 'site_id', ''))

                    start(bot, update)

                elif update.message.text == REFRESH:
                    with Shelve() as sh:
                        update.message.text = get_sql_map_name(sh.get(chat_id, 'map_id'))

                    start(bot, update)

                else:
                    try:
                        map_id = get_sql_map_id(update.message.text)
                        with Shelve() as sh:
                            sh.set(chat_id, 'map_id', map_id)

                        reply_markup = ReplyKeyboardMarkup([[KeyboardButton(CHANGE_SITE),
                                                             KeyboardButton(CHANGE_MAP),
                                                             KeyboardButton(REFRESH)]],
                                                            one_time_keyboard=True, resize_keyboard=True)

                        path, info = get_map(map_id, datetime.now())
                        log.info('path %s' % path)

                        with Shelve() as sh:
                            p = sh.get(chat_id, 'last_map')
                            if p and p == path:
                                bot.sendMessage(chat_id, text='<обновление отсутствует>', reply_markup=reply_markup)
                                return

                        bot.sendMessage(chat_id, text=info, reply_markup=reply_markup)

                        if path:
                            with open(path.encode('utf-8'), 'rb') as image:
                                bot.sendPhoto(chat_id, image, reply_markup=reply_markup)

                                with Shelve() as sh:
                                    sh.set(chat_id, 'last_map', path)
                        else:
                            bot.sendMessage(chat_id, text='<изображение отсутствует>', reply_markup=reply_markup)

                    except NoResultFound, err:

                        site_id = get_site_id(update.message.text)

                        set_user_data(chat_id, '', user_id, site_id)
                        reply_markup = ReplyKeyboardMarkup(maps_keyboard_layout(site_id, KeyboardButton),
                                                           one_time_keyboard=True, resize_keyboard=True)
                        bot.sendMessage(chat_id, text="Выберите карту", reply_markup=reply_markup)

    except Exception, err:
        log.error('start function error: %s' % str(err))
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
                with open(path.encode('utf-8'), 'rb') as image:
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


def main_hook():

    db_init()

    WEBHOOK_HOST = sys.argv[2]
    WEBHOOK_PORT = 443  # 443, 80, 88 или 8443
    WEBHOOK_LISTEN = '0.0.0.0'

    WEBHOOK_SSL_CERT = './webhook_cert.pem'
    WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

    WEBHOOK_URL = "https://%s:%d/%s" % (WEBHOOK_HOST, WEBHOOK_PORT, sys.argv[1])

    updater.start_webhook(listen=WEBHOOK_LISTEN, port=WEBHOOK_PORT,
        url_path=sys.argv[1],
        cert=WEBHOOK_SSL_CERT, key=WEBHOOK_SSL_PRIV,
        webhook_url='%s' % WEBHOOK_URL)
