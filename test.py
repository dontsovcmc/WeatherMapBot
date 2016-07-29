# -*- coding: utf-8 -*-
__author__ = 'dontsov'

from logger import log
from telegram.ext import CommandHandler, InlineQueryHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram import ForceReply, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from core import CHANGE_CONT, CHANGE_REGION, CHANGE_MAP, REFRESH, PREVIOUS_MAP, NEXT_MAP

from init import init
from core import CHANGE_CONT, CHANGE_REGION, CHANGE_MAP, REFRESH, PREVIOUS_MAP, NEXT_MAP
from core import maps_keyboard_layout, continent_keyboard_layout, region_keyboard_layout
from core import get_map_id, get_map_type_id, get_region_id, get_continent_id
from core import get_map, get_continent_name, get_region_name, get_map_type_name
from core import get_legend, get_previous_timestamp_by_path, get_next_timestamp_by_path

def test_handler(bot, update):

    from datetime import datetime

    chat_id = update.message.chat_id
    try:
        try:
            reply_markup = ReplyKeyboardMarkup([[KeyboardButton(REFRESH),
                                                 KeyboardButton(u'Погода рядом', request_location=True)]],
                                                            one_time_keyboard=True, resize_keyboard=True)

            reply_markup2 = InlineKeyboardMarkup([[InlineKeyboardButton(text=u"inline", callback_data='dgdf')]],
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
