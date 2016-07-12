# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import logging
import sys

from GisMeteoParser import EUROPE, SIBERIA, FAR_EAST, CLOUDS, OSADKI, WIND, TEMPERATURE
from GisMeteoParser import BetaMap

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

updater = Updater(token=sys.argv[1])
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Это не официальный бот сайта gismeteo.ru. Вы можете спросить меня карты погоды. /map")

start_handler = CommandHandler('start', start)
updater.dispatcher.add_handler(start_handler)

def echo(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text=update.message.text)

echo_handler = MessageHandler([Filters.text], echo)
updater.dispatcher.add_handler(echo_handler)

def map_command(bot, update):
    m = BetaMap(EUROPE, CLOUDS) #Map('Радар - МО', '647')
    m.update()
    t = m.now()
    bot.sendMessage(chat_id=update.message.chat_id, text=t)

map_handler = CommandHandler('map', map_command)
updater.dispatcher.add_handler(map_handler)


def start():
    updater.start_polling()

