import logging
import os
import time
from telegram import callbackquery, CallbackQuery
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import lib


def make_keyboard(cmd,info_list):
    keyboard = []
    temp_keyboard = []
    if cmd == "code":
        for key, value in lib.codes_dict.items():
            callback = "code&"+str(value)+"&"+key
            temp_keyboard.append(InlineKeyboardButton(key, callback_data=callback))
            if len(temp_keyboard) == 2:
                keyboard.append(temp_keyboard)
                temp_keyboard = []
        if len(temp_keyboard) != 0:
            keyboard.append(temp_keyboard)
        return keyboard
    elif type(cmd) == int:
        for item in info_list:
            calback_data = item["callback"]
            temp_keyboard.append(InlineKeyboardButton(item["button"], callback_data=calback_data))
            if len(temp_keyboard) == cmd:
                keyboard.append(temp_keyboard)
                temp_keyboard = []
        if len(temp_keyboard) != 0:
            keyboard.append(temp_keyboard)
        return keyboard
