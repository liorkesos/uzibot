
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

import helper_func


def new_client(update: Update, context: CallbackContext) -> int:
    print("hello")
    print(update)
    print(callbackquery)
    pass

def get_bn(update: Update, context: CallbackContext) -> int:
    keyboard = []
    checker_list = []
    data_dict = []
    update.message.reply_text("טוב ... סרקתי \n בוא ננסה ח.פ")
    info_list = helper_func.handler(data_dict)

    for i in info_list:
        info_dict = list(i.values())[0]
        bn = info_dict["bn"]
        if len(bn) == 0 :
            continue

        for num in bn:
            if num in checker_list:
                continue
            checker_list.append(num)
            index = bn.index(num)
            dict_name = list(i.keys())[0]
            callback_data = dict_name+"-"+str(index)
            keyboard.append([InlineKeyboardButton(num, callback_data=callback_data)])
    keyboard.append([InlineKeyboardButton("אף אחד מהם", callback_data="none")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("האם אחד מהם הוא הח.פ? \n  אם כן לחץ עליו",reply_markup=reply_markup)


