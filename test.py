# -*- coding: utf-8 -*-
__author__ = 'dontsov'

import sys

from logger import log
from telegram.ext import CommandHandler, InlineQueryHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram import ForceReply, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from init import init
from core import get_map_id, get_map_type_id
from core import get_map
from core import get_legend, get_previous_timestamp_by_path, get_next_timestamp_by_path

import unittest


#updater.dispatcher.add_handler(CallbackQueryHandler(cb_handler))
def cb_handler(bot, update):
    user_id = update.callback_query.from_user.id
    text = update.callback_query.data

    
def test_handler(bot, update):

    from datetime import datetime

    chat_id = update.message.chat_id
    try:
        try:
            reply_markup = ReplyKeyboardMarkup([[KeyboardButton(u'??'),
                                                 KeyboardButton(u'Погода рядом', request_location=True)]],
                                                            one_time_keyboard=True, resize_keyboard=True)

            reply_markup2 = InlineKeyboardMarkup([[InlineKeyboardButton(text=u"inline", callback_data='dgdf')]],
                                               resize_keyboard=True)

            map_id = 2
            path, info = get_map(map_id, datetime.utcnow())
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


class TestBot():

    def __init__(self, user_id):
        self.user_id = user_id
        self.args = {}
        self.chat_id = None

    def sendMessage(self, chat_id, **kwargs):
        self.chat_id = chat_id
        for args in kwargs:
            self.args[args] = kwargs[args]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class TestMessage():
    def __init__(self, *args, **kwargs):
        self.chat_id = kwargs.get('chat_id')


class TestUpdate():
    def __init__(self,  *args, **kwargs):
        self.message = TestMessage(kwargs.get('message'))


from telegram.update import Update

bot = TestBot('1')
update = TestUpdate(message={'chat_id': '0'})

from bot import STATE_MENU, STATE_CONT, STATE_REGION, STATE_TYPE, STATE_MAP
from bot import start_handler

class TestStart(unittest.TestCase):

    #self.assertEqual('foo'.upper(), 'FOO')

    #self.assertTrue('FOO'.isupper())
    #self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

    def test_start(self):
        self.assertEqual(start_handler(bot, update), STATE_CONT)


if __name__ == '__main__':

    unittest.main()