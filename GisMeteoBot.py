# -*- coding: utf-8 -*-
__author__ = 'doncov.eugene'

import logging
import sys

from core import WeatherSite, WeatherSites, WeatherMap
from GisMeteoParser import GisMeteoMap
from PictureMap import PictureMap

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters

from telegram import ForceReply, ReplyKeyboardMarkup, KeyboardButton


updater = Updater(token=sys.argv[1])
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

MENU, CHOOSE_SITE, CHOOSE_MAP, WATCH_MAP = range(4)

# States are saved in a dict that maps chat_id -> state
state = dict()
# Sometimes you need to save data temporarily
context = dict()
# This dict is used to store the settings value for the chat.
# Usually, you'd use persistence for this (e.g. sqlite).
values = dict()


osadki_mo = GisMeteoMap(u'МО: Осадки', '569')
radar_mo = GisMeteoMap(u'МО: Радар', '647')
osadki_russia = GisMeteoMap(u'Ц.Россия: Осадки', '572')
cloulds_russia = GisMeteoMap(u'Ц.Россия: Облачность', '568')
temp_russia = GisMeteoMap(u'Ц.Россия: T возд', '570')

change_site = WeatherMap(u'Выбор сайта', '')

meteoinfo_spb = PictureMap(u'СПБ: Радар', 'http://meteoinfo.by/radar/RUSP/RUSP_latest.png')
meteoinfo_spb_gif = PictureMap(u'СПБ: Радар (анимир)', 'http://meteoinfo.by/radar/RUSP/radar-map.gif')

weather_sites = WeatherSites([
    WeatherSite('gismeteo_ru', [osadki_mo, radar_mo, osadki_russia, cloulds_russia, temp_russia, change_site]),
    WeatherSite('meteoinfo_by', [meteoinfo_spb, meteoinfo_spb_gif])])


def start(bot, update):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    text = update.message.text
    chat_state = state.get(chat_id, MENU)
    chat_context = context.get(chat_id, None)

    # Since the handler will also be called on messages, we need to check if
    # the message is actually a command
    if chat_state == MENU and text[0] == '/':

        state[chat_id] = CHOOSE_SITE
        context[chat_id] = (user_id, '', '')

        reply_markup = ReplyKeyboardMarkup(weather_sites.keyboard_layout(),
                                           one_time_keyboard=True, resize_keyboard=True)
        bot.sendMessage(chat_id, text="Выберите сайт", reply_markup=reply_markup)

    elif chat_state == CHOOSE_SITE and chat_context and chat_context[0] == user_id:

        site = weather_sites.get(update.message.text)
        if site:
            state[chat_id] = CHOOSE_MAP
            context[chat_id] = (user_id, site, '')
            reply_markup = ReplyKeyboardMarkup(site.keyboard_layout(), one_time_keyboard=True, resize_keyboard=True)
            bot.sendMessage(chat_id, text="Выберите карту", reply_markup=reply_markup)
        else:
            state[chat_id] = CHOOSE_SITE
            context[chat_id] = (user_id, '', '')
            update.message.text = '/start'
            start(bot, update)

    elif chat_state == CHOOSE_MAP and chat_context and chat_context[0] == user_id:

        site = context[chat_id][1]
        wmap = site.get(update.message.text)

        if wmap:
            if wmap.name == change_site.name:

                state[chat_id] = MENU
                context[chat_id] = (user_id, '', '')
                update.message.text = '/start'
                start(bot, update)

            else:
                state[chat_id] = WATCH_MAP
                context[chat_id] = (user_id, site, wmap)

                wmap.update()
                reply_text = wmap.now()
                reply_markup = ReplyKeyboardMarkup([[KeyboardButton(change_site.name), KeyboardButton("Выбор карты"), KeyboardButton("Обновить")]],
                                                    one_time_keyboard=True, resize_keyboard=True)
                bot.sendMessage(chat_id, text=reply_text, reply_markup=reply_markup)
        else:
            state[chat_id] = CHOOSE_SITE
            context[chat_id] = (user_id, site, '')
            update.message.text = site.name
            start(bot, update)


    elif chat_state == WATCH_MAP and chat_context and chat_context[0] == user_id:

        if text == change_site.name:
            state[chat_id] = MENU
            update.message.text = '/start'
            start(bot, update)

        elif text == u'Выбор карты':
            state[chat_id] = CHOOSE_SITE
            update.message.text = context[chat_id][1].name
            start(bot, update)

        elif text == u'Обновить':
            state[chat_id] = CHOOSE_MAP
            update.message.text = context[chat_id][2].name
            start(bot, update)

        else: # Update
            update.message.text = '/start'
            start(bot, update)
    else:
        bot.sendMessage(chat_id,
                        text="Что-то пошло не так /start")


updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(MessageHandler([Filters.text], start))



def main():
    updater.start_polling()

