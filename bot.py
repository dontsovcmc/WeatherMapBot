# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import sys
from logger import log
from datetime import datetime, timedelta

from telegram.ext import Updater
from telegram.ext import CommandHandler, InlineQueryHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters, ConversationHandler
from telegram import ForceReply, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.inlinequeryresultlocation import InlineQueryResultLocation

from sqlalchemy.orm.exc import NoResultFound

from service import exception_info

from core import get_continent_name_id, get_region_name_id, get_type_name_id
from init import init
from core import maps_keyboard_layout, continent_keyboard_layout, region_keyboard_layout
from core import get_map_id, get_map_type_id, get_region_id, get_continent_id
from core import get_map, get_continent_name, get_region_name, get_map_type_name
from core import get_legend, get_previous_timestamp_by_path, get_next_timestamp_by_path

from storage import shelve_db, Shelve

from report import report

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

STATE_MENU, STATE_CONT, STATE_REGION, STATE_TYPE, STATE_MAP = range(5)


show_map_reply_markup = ReplyKeyboardMarkup([
    [KeyboardButton(PREVIOUS_MAP), KeyboardButton(REFRESH), KeyboardButton(NEXT_MAP)],
    [KeyboardButton(BACK), KeyboardButton(MENU)]],
    one_time_keyboard=True, resize_keyboard=True)

'''
3.  в отчет - словами
4.  БД типов карт
5.  https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/conversationbot.py
7.  подписка на обновления
8.  request_location
9.  UTC везде
'''

def start(bot, update):

    reply_keyboard = [[KeyboardButton(u'Отправить местоположение', request_location=True),
                      KeyboardButton(u'Выбрать карту')]]

    bot.sendMessage(update.message.chat_id,
                    text=u'Добрый день! Я могу отображать карты погоды'
                         u'с различных сайтов. Пришлите мне свое местоположение'
                         u'или выберите карту вручную!',
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=True))
    return STATE_CONT


def location(bot, update):
    user_id = update.message.from_user.id
    loc = update.message.location
    print "%s" % str(loc)
    # определяем карту, заоплняем структуры
    return STATE_MAP


def select_continent(bot, update):

    text = update.message.text

    if text == '/manual' or text == u'Выбрать карту':

        reply_keyboard = [[KeyboardButton(d[0])] for d in get_continent_name_id()]

        bot.sendMessage(update.message.chat_id,
                    text=u'Выберите континент',
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard), one_time_keyboard=True)
        return STATE_REGION

    return ConversationHandler.END


def continent_handler(bot, update):
    text = update.message.text

    found = [cont for cont in get_continent_name_id() if cont[0] == text]

    if found:
        with Shelve() as sh:
            sh.set(update.message.chat_id, CONTINENT, get_continent_id(text))

        reply_keyboard = [[KeyboardButton(d[0])] for d in get_region_name_id()]

        bot.sendMessage(update.message.chat_id,
                    text=u'Выберите регион',
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard), one_time_keyboard=True)
        return STATE_TYPE

    return STATE_CONT


def region_handler(bot, update):
    text = update.message.text

    found = [cont for cont in get_region_name_id() if cont[0] == text]
    if found:
        with Shelve() as sh:
            sh.set(update.message.chat_id, REGION, get_region_id(text))

        reply_keyboard = [[KeyboardButton(d[0])] for d in get_type_name_id()]

        bot.sendMessage(update.message.chat_id,
                    text=u'Выберите тип',
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard), one_time_keyboard=True)
        return STATE_MAP

    return STATE_REGION


def type_handler(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    text = update.message.text

    try:
        type_id = get_map_type_id(text)
        timestamp = datetime.now()

        with Shelve() as sh:
            sh.set(chat_id, MAPTYPE, type_id)
            map_id = get_map_id(sh.get(chat_id, REGION), type_id)
            sh.set(chat_id, MAPID, map_id)

        return send_map(bot, map_id, timestamp)

    except Exception, err:
        log.error('type_handler error: %s' % str(err))
        log.error(exception_info())
        report.track_screen(user_id, '/error')
        bot.sendMessage(chat_id, text=u"Что-то пошло не так. Начать сначала: /start")

    return STATE_REGION

def send_map(bot, update, map_id, timestamp):

    chat_id = update.message.chat_id
    user_id = update.message.from_user.id

    path, info = get_map(map_id, timestamp)
    log.info('path %s' % path)


    reply_keyboard = [[KeyboardButton(PREVIOUS_MAP), KeyboardButton(REFRESH), KeyboardButton(NEXT_MAP)],
                      [KeyboardButton(BACK), KeyboardButton(MENU)]]

    with Shelve() as sh:
        last_path = sh.get(chat_id, 'last_map')

        if last_path == path:
            bot.sendMessage(chat_id,
                            text=u'<обновление отсутствует>',
                            reply_markup=ReplyKeyboardMarkup(reply_keyboard))

            report.track_screen(user_id, '/%s/no_update' % (map_id))
        else:

            if path:
                with open(path.encode('utf-8'), 'rb') as image:
                    bot.sendPhoto(chat_id, image, caption=info.encode('utf-8'), reply_markup=show_map_reply_markup)

                    report.track_screen(user_id, '/%s' % (map_id))
                    sh.set(chat_id, 'last_map', path)
            else:
                bot.sendMessage(chat_id, text=info + u'\n<изображение отсутствует>', reply_markup=show_map_reply_markup)
                report.track_screen(user_id, '/%s/no_image' % (map_id))


def timestamp_handler(bot, update):
    text = update.message.text
    timestamp = datetime.strptime(text, '%d.%m.%Y %H:%M)') - timedelta(seconds=1)
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id




def cancel_handler(bot, update):
    return STATE_MENU


def start1(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    text = update.message.text

    shelve_db.open()

    try:
        chat_user = shelve_db.get(chat_id, USER)

        if text == '/start' or not chat_user:
            report.track_screen(user_id, '/start')
            shelve_db.set(chat_id, USER, user_id)
            shelve_db.set(chat_id, CONTINENT, None)
            shelve_db.set(chat_id, REGION, None)
            shelve_db.set(chat_id, MAPTYPE, None)

            start_reply_markup = ReplyKeyboardMarkup(continent_keyboard_layout(KeyboardButton),
                                                     one_time_keyboard=True, resize_keyboard=True)

            bot.sendMessage(chat_id, text=CHANGE_CONT, reply_markup=start_reply_markup)

        elif chat_user and chat_user == user_id:

            if text == CHANGE_CONT:
                report.track_screen(user_id, CHANGE_CONT)
                shelve_db.set(chat_id, CONTINENT, None)
                shelve_db.set(chat_id, REGION, None)
                shelve_db.set(chat_id, MAPTYPE, None)
                update.message.text = '/start'
                start(bot, update)

            elif text == CHANGE_REGION:
                report.track_screen(user_id, CHANGE_REGION)
                update.message.text = get_continent_name(shelve_db.get(chat_id, CONTINENT, ''))
                shelve_db.set(chat_id, CONTINENT, None)
                shelve_db.set(chat_id, REGION, None)
                shelve_db.set(chat_id, MAPTYPE, None)
                start(bot, update)

            elif text == CHANGE_MAP:
                report.track_screen(user_id, CHANGE_MAP)
                update.message.text = get_region_name(shelve_db.get(chat_id, REGION, ''))
                shelve_db.set(chat_id, REGION, None)
                shelve_db.set(chat_id, MAPTYPE, None)

                start(bot, update)

            elif text == REFRESH:
                report.track_screen(user_id, REFRESH)
                id = shelve_db.get(chat_id, MAPTYPE)
                if id:
                    update.message.text = get_map_type_name(id)
                else:
                    id = shelve_db.get(chat_id, REGION)
                    if id:
                        update.message.text = get_region_name(id)
                    else:
                        id = shelve_db.get(chat_id, CONTINENT)
                        if id:
                            update.message.text = get_continent_name(id)
                        else:
                            update.message.text = '/start'

                start(bot, update)

            elif text == PREVIOUS_MAP:
                report.track_screen(user_id, PREVIOUS_MAP)

                p = shelve_db.get(chat_id, 'last_map')
                if not p:
                    update.message.text = REFRESH
                    start(bot, update)

                try:
                    timestamp = get_previous_timestamp_by_path(p)
                    name = get_map_type_name(shelve_db.get(chat_id, MAPTYPE))
                    update.message.text = name + timestamp.strftime(' (%d.%m.%Y %H:%M)')
                    start(bot, update)
                except NoResultFound:
                    report.track_screen(user_id, u'<изображение отсутствует>')
                    bot.sendMessage(chat_id, text=u'\n<изображение отсутствует>', reply_markup=show_map_reply_markup)

            elif text == NEXT_MAP:
                report.track_screen(user_id, NEXT_MAP)

                p = shelve_db.get(chat_id, 'last_map')
                if not p:
                    update.message.text = REFRESH
                    start(bot, update)

                try:
                    timestamp = get_next_timestamp_by_path(p)
                    name = get_map_type_name(shelve_db.get(chat_id, MAPTYPE))
                    update.message.text = name + timestamp.strftime(' (%d.%m.%Y %H:%M)')
                    start(bot, update)

                except NoResultFound:
                    report.track_screen(user_id, u'no_image')
                    bot.sendMessage(chat_id, text=u'\n<изображение отсутствует>', reply_markup=show_map_reply_markup)

            else:
                map_type_id = shelve_db.get(chat_id, MAPTYPE)
                region_id = shelve_db.get(chat_id, REGION)
                continent_id = shelve_db.get(chat_id, CONTINENT)

                if not continent_id:

                    cont_id = get_continent_id(text)
                    shelve_db.set(chat_id, CONTINENT, cont_id)

                    reply_markup = ReplyKeyboardMarkup(region_keyboard_layout(cont_id, KeyboardButton),
                                                       one_time_keyboard=True, resize_keyboard=True)
                    bot.sendMessage(chat_id, text=CHANGE_REGION, reply_markup=reply_markup)

                    report.track_screen(user_id, '/%s' % (continent_id))

                elif not region_id:

                    region_id = get_region_id(text)
                    shelve_db.set(chat_id, REGION, region_id)

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

                    shelve_db.set(chat_id, MAPTYPE, map_type_id)
                    map_id = get_map_id(region_id, map_type_id)

                    path, info = get_map(map_id, timestamp)
                    log.info('path %s' % path)

                    p = shelve_db.get(chat_id, 'last_map')
                    if p and p == path:
                        bot.sendMessage(chat_id, text=u'<обновление отсутствует>', reply_markup=show_map_reply_markup)

                        report.track_screen(user_id, '/%s/%s/%s/%s/no_update' % (
                        continent_id, region_id, map_type_id, map_id))
                    else:

                        if path:
                            with open(path.encode('utf-8'), 'rb') as image:
                                bot.sendPhoto(chat_id, image, caption=info.encode('utf-8'), reply_markup=show_map_reply_markup)

                                report.track_screen(user_id,
                                                    '/%s/%s/%s/%s' % (continent_id, region_id, map_type_id, map_id))
                                shelve_db.set(chat_id, 'last_map', path)
                        else:
                            bot.sendMessage(chat_id, text=info + u'\n<изображение отсутствует>', reply_markup=show_map_reply_markup)
                            report.track_screen(user_id, '/%s/%s/%s/%s/no_image' % (
                            continent_id, region_id, map_type_id, map_id))

        shelve_db.close()

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



conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            STATE_MENU: [CommandHandler('start', start)],

            STATE_CONT: [MessageHandler([Filters.location], location),
                         MessageHandler([Filters.text], select_continent)],

            STATE_REGION: [MessageHandler([Filters.text], continent_handler)],

            STATE_TYPE: [MessageHandler([Filters.text], region_handler)],

            STATE_MAP: [CommandHandler('start', start),
                        MessageHandler([Filters.text], type_handler)]
        },

        fallbacks=[CommandHandler('cancel', cancel_handler)]
    )

def error(bot, update, error):
    log.warn('Update "%s" caused error "%s"' % (update, error))


def cb_handler(bot, update):
    user_id = update.callback_query.from_user.id
    text = update.callback_query.data


updater.dispatcher.add_handler(conv_handler)
#updater.dispatcher.add_handler(CommandHandler('start', start))
#updater.dispatcher.add_handler(MessageHandler([Filters.text], start))

updater.dispatcher.add_handler(CommandHandler('legend', legend_handler))
updater.dispatcher.add_handler(CommandHandler('start', start))

#updater.dispatcher.add_handler(CallbackQueryHandler(cb_handler))

updater.dispatcher.add_error_handler(error)


from test import test_handler
updater.dispatcher.add_handler(CommandHandler('test', test_handler))

