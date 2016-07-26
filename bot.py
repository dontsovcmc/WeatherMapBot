# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import sys, traceback
from logger import log


from telegram.ext import Updater
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters

from telegram import ForceReply, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup

from core import init as db_init
from core import CHANGE_CONT, CHANGE_REGION, CHANGE_MAP, REFRESH, PREVIOUS_MAP, NEXT_MAP
from core import maps_keyboard_layout, continent_keyboard_layout, region_keyboard_layout
from core import get_map_id, get_map_type_id, get_region_id, get_continent_id
from core import get_map, get_continent_name, get_region_name, get_map_type_name
from core import get_legend, get_previous_timestamp_by_path, get_next_timestamp_by_path

from datetime import datetime, timedelta
from sqlalchemy.orm.exc import NoResultFound


BOT_KEY = sys.argv[1]

updater = Updater(token=BOT_KEY)

from storage import Shelve


def exception_info():
    traceback_template = '''Traceback (most recent call last):
  File "%(filename)s", line %(lineno)s, in %(name)s
%(type)s: %(message)s\n'''

    exc_type, exc_value, exc_traceback = sys.exc_info()
    traceback_details = {
         'filename': exc_traceback.tb_frame.f_code.co_filename,
         'lineno': exc_traceback.tb_lineno,
         'name': exc_traceback.tb_frame.f_code.co_name,
         'type': exc_type.__name__,
         'message': exc_value.message}
    del(exc_type, exc_value, exc_traceback)
    return traceback.format_exc() + '\n' + traceback_template % traceback_details


def set_user_data(chat_id, state, user_id='', cont_id='', region_id='', maptype_id=''):
    with Shelve() as sh:
        sh.set(chat_id, 'state', state)
        sh.set(chat_id, 'user_id', user_id)
        sh.set(chat_id, 'cont_id', cont_id)
        sh.set(chat_id, 'region_id', region_id)
        sh.set(chat_id, 'maptype_id', maptype_id)


show_map_reply_markup = ReplyKeyboardMarkup([
    [KeyboardButton(PREVIOUS_MAP), KeyboardButton(REFRESH), KeyboardButton(NEXT_MAP)],
    [KeyboardButton(CHANGE_CONT), KeyboardButton(CHANGE_REGION), KeyboardButton(CHANGE_MAP)]],
    one_time_keyboard=True, resize_keyboard=True)


def start(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    text = update.message.text

    try:
        with Shelve() as sh:
            chat_user = sh.get(chat_id, 'user_id', None)

        if text == '/start' or not chat_user:
            set_user_data(chat_id, '', user_id)

            reply_markup = ReplyKeyboardMarkup(continent_keyboard_layout(KeyboardButton), one_time_keyboard=True, resize_keyboard=True)
            bot.sendMessage(chat_id, text=CHANGE_CONT, reply_markup=reply_markup)

        elif chat_user and chat_user == user_id:

            if update.message.text == CHANGE_CONT:

                set_user_data(chat_id, '', user_id)
                update.message.text = '/start'
                start(bot, update)

            elif update.message.text == CHANGE_REGION:

                with Shelve() as sh:
                    update.message.text = get_continent_name(sh.get(chat_id, 'cont_id', ''))
                    sh.set(chat_id, 'cont_id', '')

                start(bot, update)

            elif update.message.text == CHANGE_MAP:

                with Shelve() as sh:
                    update.message.text = get_region_name(sh.get(chat_id, 'region_id', ''))
                    sh.set(chat_id, 'region_id', '')

                start(bot, update)

            elif update.message.text == REFRESH:
                with Shelve() as sh:
                    id = sh.get(chat_id, 'maptype_id')
                    if id:
                        update.message.text = get_map_type_name(id)
                    else:
                        id = sh.get(chat_id, 'region_id')
                        if id:
                            update.message.text = get_region_name(id)
                        else:
                            id = sh.get(chat_id, 'cont_id')
                            if id:
                                update.message.text = get_continent_name(id)
                            else:
                                update.message.text = '/start'

                start(bot, update)

            elif update.message.text == PREVIOUS_MAP:
                with Shelve() as sh:
                    p = sh.get(chat_id, 'last_map')
                    if not p:
                        update.message.text = REFRESH
                        start(bot, update)

                    try:
                        timestamp = get_previous_timestamp_by_path(p)
                        name = get_map_type_name(sh.get(chat_id, 'maptype_id'))
                        update.message.text = name + timestamp.strftime(' (%d.%m.%Y %H:%M)')
                        start(bot, update)
                    except NoResultFound:
                        bot.sendMessage(chat_id, text=u'\n<изображение отсутствует>', reply_markup=show_map_reply_markup)

            elif update.message.text == NEXT_MAP:
                with Shelve() as sh:
                    p = sh.get(chat_id, 'last_map')
                    if not p:
                        update.message.text = REFRESH
                        start(bot, update)

                    try:
                        timestamp = get_next_timestamp_by_path(p)
                        name = get_map_type_name(sh.get(chat_id, 'maptype_id'))
                        update.message.text = name + timestamp.strftime(' (%d.%m.%Y %H:%M)')
                        start(bot, update)
                    except NoResultFound:
                        bot.sendMessage(chat_id, text=u'\n<изображение отсутствует>', reply_markup=show_map_reply_markup)

            else:
                with Shelve() as sh:
                    map_type_id = sh.get(chat_id, 'map_type_id')
                    region_id = sh.get(chat_id, 'region_id')
                    continent_id = sh.get(chat_id, 'cont_id')

                    if not continent_id:

                        cont_id = get_continent_id(update.message.text)
                        with Shelve() as sh:
                            sh.set(chat_id, 'cont_id', cont_id)

                        reply_markup = ReplyKeyboardMarkup(region_keyboard_layout(cont_id, KeyboardButton),
                                                           one_time_keyboard=True, resize_keyboard=True)
                        bot.sendMessage(chat_id, text=CHANGE_CONT, reply_markup=reply_markup)

                    elif not region_id:

                        region_id = get_region_id(update.message.text)
                        with Shelve() as sh:
                            sh.set(chat_id, 'region_id', region_id)

                        reply_markup = ReplyKeyboardMarkup(maps_keyboard_layout(region_id, KeyboardButton),
                                                           one_time_keyboard=True, resize_keyboard=True)
                        bot.sendMessage(chat_id, text=CHANGE_REGION, reply_markup=reply_markup)

                    elif not map_type_id:

                        if len(update.message.text.split(' (')) != 2:
                            map_type_id = get_map_type_id(update.message.text)
                            timestamp = datetime.now()
                        else:
                            map_type_name, timestr = update.message.text.split(' (')
                            map_type_id = get_map_type_id(map_type_name)
                            timestamp = datetime.strptime(timestr, '%d.%m.%Y %H:%M)') - timedelta(seconds=1)

                        sh.set(chat_id, 'maptype_id', map_type_id)
                        map_id = get_map_id(region_id, map_type_id)
                        path, info = get_map(map_id, timestamp)
                        log.info('path %s' % path)

                        with Shelve() as sh:
                            p = sh.get(chat_id, 'last_map')
                            if p and p == path:
                                bot.sendMessage(chat_id, text=u'<обновление отсутствует>', reply_markup=show_map_reply_markup)
                                return

                        if path:
                            with open(path.encode('utf-8'), 'rb') as image:
                                bot.sendPhoto(chat_id, image, caption=info.encode('utf-8'), reply_markup=show_map_reply_markup)

                                with Shelve() as sh:
                                    sh.set(chat_id, 'last_map', path)
                        else:
                            bot.sendMessage(chat_id, text=info + u'\n<изображение отсутствует>', reply_markup=show_map_reply_markup)

    except Exception, err:
        log.error('start function error: %s' % str(err))
        log.error(exception_info())
        bot.sendMessage(chat_id, text=u"Что-то пошло не так. Начать сначала: /start")


def legend_handler(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    try:
        with Shelve() as sh:
            map_type_id = sh.get(chat_id, 'maptype_id', None)
            region_id = sh.get(chat_id, 'region_id', None)
            map_id = get_map_id(region_id, map_type_id)
        if map_id:
            info = get_legend(map_id)
            bot.sendMessage(chat_id, text=info, reply_markup=show_map_reply_markup)
        else:
            update.message.text = '/start'
            set_user_data(chat_id, '', user_id)
            start(bot, update)

    except Exception, err:
        log.error('legend_handler error: %s' % str(err))
        update.message.text = '/start'
        start(bot, update)


def test_handler(bot, update):

    from datetime import datetime

    chat_id = update.message.chat_id
    try:
        try:
            reply_markup = ReplyKeyboardMarkup([[KeyboardButton(CHANGE_CONT),
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
                bot.sendMessage(chat_id, text=u'<изображение отсутствует>', reply_markup=reply_markup)

        except Exception, err:
            log.error(err)
            bot.sendMessage(chat_id, text=u'<internal error>', reply_markup=reply_markup)

    except Exception, err:
        log.error(err)
        bot.sendMessage(chat_id, text=u'<internal error>', reply_markup=reply_markup)



updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler([Filters.text], start))
updater.dispatcher.add_handler(CommandHandler('legend', legend_handler))

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
