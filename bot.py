#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from auth import token
from telegram import ReplyKeyboardMarkup
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, TYPING_CHOICE= range(2)

reply_keyboard = [['Ver apuestas','Ver estadísticas'],
                  ['Cerrar por hoy']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)


def facts_to_str(user_data):
    message = 'Las apuestas del día de hoy fueron: \n'
    for pos,apuesta in enumerate(user_data.get('Apuestas', [])):
        message += str(pos+1)+". "+ apuesta + "\n"

    apuestas = user_data.get('Apuestas', [])
    acertadas = 0
    erradas = 0
    indefinidas = 0
    for apuesta in apuestas:
        if '✅' in apuesta:
            acertadas+=1
        elif '❌' in apuesta:
            erradas+=1
        else:
            indefinidas+=1
    porc = 0 if erradas+acertadas == 0 else round(acertadas * 100 /(acertadas+erradas),2)
    message += "Las estadísticas del día de hoy fueron: \n"
    message += "Acertadas = {} Erradas = {}\n Indefinidas = {}\n Acierto = {}%".format(acertadas,erradas,indefinidas,porc)

    return message

def start(update, context):
    update.message.reply_text(
        "Hola, soy tu asistente de apuestas.\n"+
        """Para agregar tu apuesta escribe "Agregar apuesta"+ la información de la apuesta.\n"""+
        """Para modificar una apuesta escribe "Modificar apuesta" + la posición de la apuesta a modificar y el nuevo estado de la apuesta ('g' para ganada o 'p' para perdida).\n"""+
        """Para eliminar una apuesta escribe "Eliminar apuesta" y la posición de la apuesta a eliminar.\n"""
        """Para ver las apuestas escribe "Ver apuestas".\n"""+
        """Para ver las estadísticas escribe "Ver estadísticas".\n""" +
        """Para cerrar por hoy escribe "Cerrar por hoy".""",
        reply_markup=markup)
    return CHOOSING

def regular_choice(update, context):
    text = update.message.text
    context.user_data['choice'] = text

    if 'Agregar apuesta' in text:
        addBet(context,text.replace("Agregar apuesta ",""))
        update.message.reply_text("Hecho!",
                                  reply_markup=markup)
    elif 'Modificar apuesta' in text:
        text = text.replace("Modificar apuesta ", "")
        pos = int(text.split(" ")[0])
        status = text.split(" ")[1]
        updateBet(context, update, pos,status)
        update.message.reply_text("Hecho!",
                                  reply_markup=markup)

    elif 'Eliminar apuesta' in text:
        text = text.replace("Eliminar apuesta ","")
        pos = int(text)
        removeBet(context,update,pos)
        update.message.reply_text("Hecho!",
                                  reply_markup=markup)

    return CHOOSING

def addBet(context, text):
    lista = context.user_data.get("Apuestas", [])
    lista.append(text)
    context.user_data['Apuestas'] = lista
    return

def removeBet(context,update, pos):
    user_data = context.user_data
    lista = user_data.get("Apuestas", [])
    if len(lista) == 0:
        update.message.reply_text("No hay apuestas para eliminar",
                                  reply_markup=markup)
        return CHOOSING
    else:
        if pos > len(lista):
            update.message.reply_text("Posición inválida. Ingrese una posición válida",
                                      reply_markup=markup)
            return TYPING_CHOICE
        else:
            context.user_data['Apuestas'].remove(user_data['Apuestas'][pos - 1])
    return

def updateBet(context,update,pos,status):
    lista = context.user_data.get("Apuestas", [])
    if len(lista) == 0:
        update.message.reply_text("No hay apuestas para modificar",
                                  reply_markup=markup)
        return CHOOSING
    else:
        if pos > len(lista):
            update.message.reply_text("Posición inválida. Ingrese una posición válida",
                                      reply_markup=markup)
            return TYPING_CHOICE

        else:
            if '✅' in context.user_data["Apuestas"][int(pos-1)]:
                context.user_data["Apuestas"][int(pos - 1)] = context.user_data["Apuestas"][int(pos - 1)].replace(' ✅','')
            elif '❌' in context.user_data["Apuestas"][int(pos-1)]:
                context.user_data["Apuestas"][int(pos - 1)] = context.user_data["Apuestas"][int(pos - 1)].replace(' ❌','')
            if status.lower() == "g":
                status = '✅'
            else:
                status = '❌'
            context.user_data["Apuestas"][int(pos-1)] += " "+status
    return

def done(update, context):
    user_data = context.user_data
    if 'choice' in user_data:
        del user_data['choice']

    update.message.reply_text("{}\n"
                              "Hasta mañana!".format(facts_to_str(user_data)))
    user_data.clear()
    return ConversationHandler.END

def apuestas(update,context):
    user_data = context.user_data
    message = 'Las apuestas del día de hoy son: \n'
    for pos,apuesta in enumerate(user_data.get('Apuestas',[])):
        message += str(pos+1)+". "+ apuesta + "\n"
    update.message.reply_text(message,
                                  reply_markup=markup)
    return CHOOSING

def stats(update,context):
    apuestas = context.user_data.get('Apuestas',[])
    acertadas = 0
    erradas = 0
    indefinidas = 0
    for apuesta in apuestas:
        if '✅' in apuesta:
            acertadas+=1
        elif '❌' in apuesta:
            erradas+=1
        else:
            indefinidas+=1
    porc = 0 if erradas+acertadas == 0 else round(acertadas * 100 /(acertadas+erradas),2)
    message = "Acertadas = {} Erradas = {}\n Indefinidas = {}\n Acierto = {}%".format(acertadas,erradas,indefinidas,porc)

    update.message.reply_text(message)
    return CHOOSING


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(token, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states CHOOSING, TYPING_CHOICE and TYPING_REPLY
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            CHOOSING: [MessageHandler(Filters.regex('^(Agregar apuesta \w*( \w*)*|Quitar apuesta \w*( \w*)*|Modificar apuesta \w*( \w*)*)$'),
                                      regular_choice),
                       MessageHandler(Filters.regex('^Ver apuestas'), apuestas),
                       MessageHandler(Filters.regex('^Ver estadísticas'), stats),
                       ],

            TYPING_CHOICE: [MessageHandler(Filters.text,
                                           regular_choice)
                            ],
        },
        fallbacks = [MessageHandler(Filters.regex('^Cerrar por hoy'), done),]

    )

    dp.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()