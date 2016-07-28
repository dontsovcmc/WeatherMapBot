# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import sys
from logger import log
from datetime import datetime, timedelta

from telegram.ext import Updater
from telegram.ext import CommandHandler, InlineQueryHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram import ForceReply, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.inlinequeryresultlocation import InlineQueryResultLocation

from sqlalchemy.orm.exc import NoResultFound

from service import exception_info

from init import init
from core import CHANGE_CONT, CHANGE_REGION, CHANGE_MAP, REFRESH, PREVIOUS_MAP, NEXT_MAP
from core import maps_keyboard_layout, continent_keyboard_layout, region_keyboard_layout
from core import get_map_id, get_map_type_id, get_region_id, get_continent_id
from core import get_map, get_continent_name, get_region_name, get_map_type_name
from core import get_legend, get_previous_timestamp_by_path, get_next_timestamp_by_path

from storage import Shelve

from report import report

updater = Updater(token=sys.argv[1])

USER = 'user_id'
MAPTYPE = 'maptype_id'
CONTINENT = 'cont_id'
REGION = 'region_id'

show_map_reply_markup = ReplyKeyboardMarkup([
    [KeyboardButton(PREVIOUS_MAP), KeyboardButton(REFRESH), KeyboardButton(NEXT_MAP)],
    [KeyboardButton(CHANGE_CONT), KeyboardButton(CHANGE_REGION), KeyboardButton(CHANGE_MAP)]],
    one_time_keyboard=True, resize_keyboard=True)

'''
3.  в отчет - словами
4.  БД типов карт
5.  https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/conversationbot.py
7.  подписка на обновления
8.  request_location
'''


def start(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    text = update.message.text


    try:
        with Shelve() as sh:
            chat_user = sh.get(chat_id, USER)

            if text == '/start' or not chat_user:
                report.track_screen(user_id, '/start')
                sh.set(chat_id, USER, user_id)
                sh.set(chat_id, CONTINENT, None)
                sh.set(chat_id, REGION, None)
                sh.set(chat_id, MAPTYPE, None)

                start_reply_markup = ReplyKeyboardMarkup(continent_keyboard_layout(KeyboardButton),
                                                         one_time_keyboard=True, resize_keyboard=True)

                bot.sendMessage(chat_id, text=CHANGE_CONT, reply_markup=start_reply_markup)

            elif chat_user and chat_user == user_id:

                if text == CHANGE_CONT:
                    report.track_screen(user_id, CHANGE_CONT)
                    sh.set(chat_id, CONTINENT, None)
                    sh.set(chat_id, REGION, None)
                    sh.set(chat_id, MAPTYPE, None)
                    update.message.text = '/start'
                    start(bot, update)

                elif text == CHANGE_REGION:
                    report.track_screen(user_id, CHANGE_REGION)
                    update.message.text = get_continent_name(sh.get(chat_id, CONTINENT, ''))
                    sh.set(chat_id, CONTINENT, None)
                    sh.set(chat_id, REGION, None)
                    sh.set(chat_id, MAPTYPE, None)
                    start(bot, update)

                elif text == CHANGE_MAP:
                    report.track_screen(user_id, CHANGE_MAP)
                    update.message.text = get_region_name(sh.get(chat_id, REGION, ''))
                    sh.set(chat_id, REGION, None)
                    sh.set(chat_id, MAPTYPE, None)

                    start(bot, update)

                elif text == REFRESH:
                    report.track_screen(user_id, REFRESH)
                    id = sh.get(chat_id, MAPTYPE)
                    if id:
                        update.message.text = get_map_type_name(id)
                    else:
                        id = sh.get(chat_id, REGION)
                        if id:
                            update.message.text = get_region_name(id)
                        else:
                            id = sh.get(chat_id, CONTINENT)
                            if id:
                                update.message.text = get_continent_name(id)
                            else:
                                update.message.text = '/start'

                    start(bot, update)

                elif text == PREVIOUS_MAP:
                    report.track_screen(user_id, PREVIOUS_MAP)

                    p = sh.get(chat_id, 'last_map')
                    if not p:
                        update.message.text = REFRESH
                        start(bot, update)

                    try:
                        timestamp = get_previous_timestamp_by_path(p)
                        name = get_map_type_name(sh.get(chat_id, MAPTYPE))
                        update.message.text = name + timestamp.strftime(' (%d.%m.%Y %H:%M)')
                        start(bot, update)
                    except NoResultFound:
                        report.track_screen(user_id, u'<изображение отсутствует>')
                        bot.sendMessage(chat_id, text=u'\n<изображение отсутствует>', reply_markup=show_map_reply_markup)

                elif text == NEXT_MAP:
                    report.track_screen(user_id, NEXT_MAP)

                    p = sh.get(chat_id, 'last_map')
                    if not p:
                        update.message.text = REFRESH
                        start(bot, update)

                    try:
                        timestamp = get_next_timestamp_by_path(p)
                        name = get_map_type_name(sh.get(chat_id, MAPTYPE))
                        update.message.text = name + timestamp.strftime(' (%d.%m.%Y %H:%M)')
                        start(bot, update)

                    except NoResultFound:
                        report.track_screen(user_id, u'no_image')
                        bot.sendMessage(chat_id, text=u'\n<изображение отсутствует>', reply_markup=show_map_reply_markup)

                else:
                    map_type_id = sh.get(chat_id, MAPTYPE)
                    region_id = sh.get(chat_id, REGION)
                    continent_id = sh.get(chat_id, CONTINENT)

                    if not continent_id:

                        cont_id = get_continent_id(text)
                        sh.set(chat_id, CONTINENT, cont_id)

                        reply_markup = ReplyKeyboardMarkup(region_keyboard_layout(cont_id, KeyboardButton),
                                                           one_time_keyboard=True, resize_keyboard=True)
                        bot.sendMessage(chat_id, text=CHANGE_REGION, reply_markup=reply_markup)

                        report.track_screen(user_id, '/%s' % (continent_id))

                    elif not region_id:

                        region_id = get_region_id(text)
                        sh.set(chat_id, REGION, region_id)

                        reply_markup = ReplyKeyboardMarkup(maps_keyboard_layout(region_id, KeyboardButton),
                                                           one_time_keyboard=True, resize_keyboard=True)
                        bot.sendMessage(chat_id, text=CHANGE_MAP, reply_markup=reply_markup)

                        report.track_screen(user_id, '/%s/%s' % (continent_id, region_id))

                    else: # not map_type_id

                        if len(update.message.text.split(' (')) != 2:
                            map_type_id = get_map_type_id(update.message.text)
                            timestamp = datetime.now()
                        else:
                            map_type_name, timestr = update.message.text.split(' (')
                            map_type_id = get_map_type_id(map_type_name)
                            timestamp = datetime.strptime(timestr, '%d.%m.%Y %H:%M)') - timedelta(seconds=1)

                        report.track_screen(user_id, '/%s/%s/%s' % (continent_id, region_id, map_type_id))

                        sh.set(chat_id, MAPTYPE, map_type_id)
                        map_id = get_map_id(region_id, map_type_id)

                        path, info = get_map(map_id, timestamp)
                        log.info('path %s' % path)

                        p = sh.get(chat_id, 'last_map')
                        if p and p == path:
                            bot.sendMessage(chat_id, text=u'<обновление отсутствует>', reply_markup=show_map_reply_markup)

                            report.track_screen(user_id, '/%s/%s/%s/%s/no_update' % (
                            continent_id, region_id, map_type_id, map_id))
                            return

                        if path:
                            with open(path.encode('utf-8'), 'rb') as image:
                                bot.sendPhoto(chat_id, image, caption=info.encode('utf-8'), reply_markup=show_map_reply_markup)

                                report.track_screen(user_id,
                                                    '/%s/%s/%s/%s' % (continent_id, region_id, map_type_id, map_id))
                                sh.set(chat_id, 'last_map', path)
                        else:
                            bot.sendMessage(chat_id, text=info + u'\n<изображение отсутствует>', reply_markup=show_map_reply_markup)
                            report.track_screen(user_id, '/%s/%s/%s/%s/no_image' % (
                            continent_id, region_id, map_type_id, map_id))

    except Exception, err:
        log.error('start function error: %s' % str(err))
        log.error(exception_info())
        report.track_screen(user_id, '/error')
        bot.sendMessage(chat_id, text=u"Что-то пошло не так. Начать сначала: /start")


def legend_handler(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    try:
        with Shelve() as sh:
            chat_user = sh.get(chat_id, USER)
            map_type_id = sh.get(chat_id, MAPTYPE)
            region_id = sh.get(chat_id, REGION)
            map_id = get_map_id(region_id, map_type_id)

            if map_id and chat_user and chat_user == user_id:
                info = get_legend(map_id)
                bot.sendMessage(chat_id, text=info, reply_markup=show_map_reply_markup)
            else:
                update.message.text = '/start'
                sh.set(chat_id, CONTINENT, None)
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
            reply_markup = ReplyKeyboardMarkup([[KeyboardButton(REFRESH),
                                                 KeyboardButton(u'Погода рядом', request_location=True)]],
                                                            one_time_keyboard=True, resize_keyboard=True)

            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text=u"inline", callback_data='dgdf')]],
                                               resize_keyboard=True)

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


def error(bot, update, error):
    log.warn('Update "%s" caused error "%s"' % (update, error))

def inline_handler(bot, update):
    pass

def cb_handler(bot, update):
    user_id = update.message.from_user.id
    text = update.callback_query.data
    pass

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler([Filters.text], start))
updater.dispatcher.add_handler(CommandHandler('legend', legend_handler))

updater.dispatcher.add_handler(CommandHandler('test', test_handler))

updater.dispatcher.add_handler(CallbackQueryHandler(cb_handler))

updater.dispatcher.add_handler(InlineQueryHandler(inline_handler))
updater.dispatcher.add_error_handler(error)


def main(hook=False):

    init()

    if not hook:
        updater.start_polling()
    else:
        WEBHOOK_HOST = sys.argv[3]
        WEBHOOK_PORT = 443  # 443, 80, 88 или 8443
        WEBHOOK_LISTEN = '0.0.0.0'

        WEBHOOK_SSL_CERT = './webhook_cert.pem'
        WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

        WEBHOOK_URL = "https://%s:%d/%s" % (WEBHOOK_HOST, WEBHOOK_PORT, sys.argv[1])

        updater.start_webhook(listen=WEBHOOK_LISTEN, port=WEBHOOK_PORT,
            url_path=sys.argv[1],
            cert=WEBHOOK_SSL_CERT, key=WEBHOOK_SSL_PRIV,
            webhook_url='%s' % WEBHOOK_URL)


