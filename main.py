import time

import telegram
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, \
    ConversationHandler, CallbackQueryHandler, PicklePersistence

from ban import ban_button, ban
from constants import BOT_TOKEN, LOCATION, DATE, TIME, GAME_FORMAT, ENTRIES_CASH_GAME, ENTRIES_TOURNAMENT, STAKE, \
    REGEXES, TABLE_ID_PREFIX, BAN_PROPOSAL_ID_PREFIX, REGISTER, OPEN_REGISTRATION
from new_table import location, receive_date, receive_time, game_format, entries, stake, abort, new_table, wrong_data, \
    table_button, register, open_registration
from strings import ngb_main_startGreet, ngb_main_startMessage, ngb_main_help

persistence = PicklePersistence(filename='database')
updater = Updater(BOT_TOKEN, persistence=persistence, use_context=True)
dispatcher = updater.dispatcher

are_handlers_set = False


def webhook(request):
    if request.method == "POST":
        set_handlers()
        update = Update.de_json(request.get_json(force=True), updater.bot)
        dispatcher.process_update(update)
    return "ok"


def test() -> None:
    set_handlers()
    updater.start_polling()
    updater.idle()


def set_handlers():
    global are_handlers_set
    if not are_handlers_set:
        dispatcher.add_handler(CommandHandler('start', start))
        dispatcher.add_handler(CommandHandler('help', help))

        # dispatcher.add_handler(CommandHandler('test', test_message))
        dispatcher.add_handler(CommandHandler('ban', ban))

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('newtable', new_table)],
            states={
                LOCATION: [MessageHandler(Filters.text & ~Filters.command, location)],
                DATE: [MessageHandler(Filters.regex(REGEXES['date']), receive_date)],
                TIME: [MessageHandler(Filters.regex(REGEXES['time']), receive_time)],
                GAME_FORMAT: [MessageHandler(Filters.regex(REGEXES['game_formats']), game_format)],
                ENTRIES_CASH_GAME: [MessageHandler(Filters.regex(REGEXES['number_of_cash_game_players']), entries)],
                ENTRIES_TOURNAMENT: [MessageHandler(Filters.regex(REGEXES['number_of_tournament_players']), entries)],
                STAKE: [MessageHandler(Filters.regex(REGEXES['stakes']), stake)],
                REGISTER: [MessageHandler(Filters.regex(REGEXES['registration_options']), register)],
                OPEN_REGISTRATION: [MessageHandler(Filters.regex(REGEXES['open_registration']), open_registration)]
            },
            fallbacks=[
                MessageHandler(Filters.text & ~Filters.command, wrong_data),
                CommandHandler('abort', abort)
            ],
            persistent=True,
            name='conversation'
        )

        dispatcher.add_handler(conv_handler)
        dispatcher.add_handler(CallbackQueryHandler(button))

        are_handlers_set = True


def test_message(update: Update, context: CallbackContext):
    return update.effective_chat.id


def start(update: Update, context: CallbackContext):
    if update.message.chat.type != 'private':
        return

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING, timeout=1)
    time.sleep(2)
    update.message.reply_text(
        text=ngb_main_startGreet
    )
    time.sleep(1)
    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=telegram.ChatAction.TYPING, timeout=1)
    time.sleep(5)
    update.message.reply_text(
        text=ngb_main_startMessage
    )


def help(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=ngb_main_help,
        parse_mode=ParseMode.HTML
    )


def button(update: Update, context: CallbackContext):
    callback_query_data = update.callback_query.data
    if callback_query_data.startswith(TABLE_ID_PREFIX):
        table_button(update, context)
    elif callback_query_data.startswith(BAN_PROPOSAL_ID_PREFIX):
        ban_button(update, context)
    else:
        return


if __name__ == "__main__":
    test()
