import logging
import os
import time
from telegram import callbackquery, CallbackQuery
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, InlineKeyboardButton,\
    InlineKeyboardMarkup,KeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
import lib
import helper_func

import bot_apps
import bot_side_func

updater = Updater(token="5468707508:AAErO58v6T02oozM6GatiQX3nOU1h17pMbQ", use_context=True)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
dispatcher = updater.dispatcher
first, handler, db, forth = range(4)





def menu(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    user_name = user.username
    update.message.reply_text(
        "START",
        reply_markup=ReplyKeyboardMarkup(
            [["/start"]], one_time_keyboard=True,resize_keyboard=True
        ),
    )


    update.message.reply_text("שלום " + user_name)
    update.message.reply_text("שלח לי קבלה אני אנסה לקרוא")
    context.chat_data["check dict"] = lib.check_dict
    return first

def pdf_handler(update: Update, context: CallbackContext) -> int:

    update.message.reply_text("קיבלתי מסמך")
    file_name = update.message.document.file_name
    download_path = lib.downloads_path + file_name
    file = update.message.document.get_file()
    file.download(download_path)
    update.message.reply_text("downloaded")
    data_dict = {"path":download_path,"name":file_name}
    update.message.reply_text("סורק....")
    info_list = helper_func.handler(data_dict)
    info_list.append(file_name)

    context.chat_data["info list"] = info_list
    keyboard = []
    temp_for_keyboard = []
    clients_list = helper_func.db_query("clients","name")
    if len(clients_list) == 0:
        update.message.reply_text("אין לקוחות ברשימת הלקוחות ")
        keyboard =[[InlineKeyboardButton("לקוח חדש ",callback_data = "new")]]
        reply_markup = InlineKeyboardMarkup(keyboard,one_time_keyboard=False)
        update.message.reply_text("לחץ בכדי להתחיל", reply_markup=reply_markup)
        return handler

    else:
        for client in clients_list:
            temp_for_keyboard.append([InlineKeyboardButton(client, callback_data=client)])
        keyboard.append(temp_for_keyboard)
        keyboard.append([InlineKeyboardButton("לקוח חדש", callback_data="new")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text("הנה רשימת הלקוחות",reply_markup=reply_markup)






def photo_handler(update: Update, context: CallbackContext) -> int:
    update.message.reply_text("קיבלתי תמונה")



def callback_handler(update: Update, context: CallbackContext) -> int:

    chat_id = update["callback_query"]["message"]["chat"]["id"]
    check_dict = context.chat_data["check dict"]
    info_list = context.chat_data["info list"]
    choice = update["callback_query"]["data"]
    if choice != "none" and choice !="new":
        item_list = context.chat_data["item list"]
        temp_list = choice.split("&")
        key = temp_list[0]
        delimiter = temp_list[1]
        if key != "code":
            answer = helper_func.get_answer(item_list,delimiter)
        else:
            answer = temp_list[2]
        check_dict[key] = {"choice":str(answer),"delimiter":delimiter}
    elif choice == "none":
        context.bot.send_message(chat_id=chat_id, text="טוב   חבל שלא מצאתי")
        context.bot.send_message(chat_id=chat_id,
                                 text="תרשום לי בבקשה את השם ואשמור אותו לעד " + lib.emoji_dict["wink"])
        return handler

    for i in check_dict:
        if check_dict[i] == "":
            buttons_in_a_row = 2
            if i == "description":
                buttons_in_a_row = 1

            message = "עכשיו נבחר "+lib.menu_dict[i]
            context.bot.send_message(chat_id=chat_id, text=message)
            item_list = helper_func.get_info(info_list, i)
            context.chat_data["item list"] = item_list
            keyboard = []
            list_for_keyboard = []
            for item in item_list:
                calback_data = i +"&"+ item["delimiter"]
                dict_for_keyboard_list = {"callback":calback_data,"button":item["info"]}
                list_for_keyboard.append(dict_for_keyboard_list)

            keyboard = bot_apps.make_keyboard(buttons_in_a_row,list_for_keyboard)
            keyboard.append([InlineKeyboardButton("אף אחד מהם " + lib.emoji_dict["sad"], callback_data="none")])

            reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=False)
            text = "האם אחד מהם הוא ה" + lib.menu_dict[i]
            context.bot.send_message(chat_id=chat_id, text=text,reply_markup=reply_markup)
            return handler
        elif i == "code" and check_dict["code"] == "123":
            keyboard = bot_apps.make_keyboard("code","")
            reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=False)
            context.bot.send_message(chat_id=chat_id, text="בחר קוד פקודה",reply_markup=reply_markup)

            return handler
    for key,value in check_dict.items():
        message = key +":"+ value["choice"]
        context.bot.send_message(chat_id = chat_id,text = message)
    keyboard = [[InlineKeyboardButton(lib.emoji_dict["like"], callback_data="save"),
                 InlineKeyboardButton(lib.emoji_dict["dislike"], callback_data="stop")]]
    reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id=chat_id, text="אפשר לשמור?", reply_markup=reply_markup)

    return db


def name_text_handler(update: Update, context: CallbackContext) -> int:
    text = update["message"]["text"]
    context.chat_data["name"] = text
    check_dict = context.chat_data["check dict"]
    info_list = context.chat_data["info list"]
    for key in check_dict:
        if check_dict[key] == "":
            update.message.reply_text("מעולה אני אשמור אותו")
            check_dict[key] = {"choice": str(text), "delimiter": "subbmited by user"}
            keyboard =[[InlineKeyboardButton( lib.emoji_dict["like"], callback_data="new"),InlineKeyboardButton( lib.emoji_dict["dislike"], callback_data="none")]]
            reply_markup = InlineKeyboardMarkup(keyboard, one_time_keyboard=True)
            update.message.reply_text("\n שומר למסד הנתונים "+ str(text), reply_markup=reply_markup)
            return handler

def insert_to_db(update: Update, context: CallbackContext) -> int:
    chat_id = update["callback_query"]["message"]["chat"]["id"]
    check_dict = context.chat_data["check dict"]
    choice = update["callback_query"]["data"]
    print(choice)







def error_handler(update: Update, context: CallbackContext) -> int:
    chat_id = update.callback_query.message.chat.id
    context.bot.send_message(chat_id=chat_id, text="למקרה שלחצת סתם על כפתור"
                                                   "\n"
                                                   "לחץ על start")
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    print("something went wrong")
    pass


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", menu)],
    states={
        first: [MessageHandler(Filters.document, pdf_handler),
                MessageHandler(Filters.photo, photo_handler)
                ],
        handler: [CallbackQueryHandler(callback_handler),
                MessageHandler(Filters.text, name_text_handler)],
        db: [CallbackQueryHandler(insert_to_db),
                ],
        forth: [MessageHandler(Filters.location, menu)]

    },
    fallbacks=[CommandHandler('cancel', error_handler)],
)

dispatcher.add_handler(conv_handler)

updater.start_polling()
updater.idle()