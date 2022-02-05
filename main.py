import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, \
    ConversationHandler, CallbackQueryHandler

from ban import ban_button, ban
from constants import BOT_TOKEN, LOCATION, DATE, TIME, GAME_FORMAT, ENTRIES_CASH_GAME, ENTRIES_TOURNAMENT, STAKE, \
    REGEXES, TABLE_ID_PREFIX, BAN_PROPOSAL_ID_PREFIX
from new_table import location, receive_date, receive_time, game_format, entries, stake, abort, new_table, wrong_data, \
    table_button

updater = Updater(BOT_TOKEN)
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
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('newtable', new_table)],
            states={
                LOCATION: [MessageHandler(Filters.text & ~Filters.command, location)],
                DATE: [MessageHandler(Filters.regex(REGEXES['date']), receive_date)],
                TIME: [MessageHandler(Filters.regex(REGEXES['time']), receive_time)],
                GAME_FORMAT: [MessageHandler(Filters.regex(REGEXES['game_formats']), game_format)],
                ENTRIES_CASH_GAME: [MessageHandler(Filters.regex(REGEXES['number_of_cash_game_players']), entries)],
                ENTRIES_TOURNAMENT: [MessageHandler(Filters.regex(REGEXES['number_of_tournament_players']), entries)],
                STAKE: [MessageHandler(Filters.regex(REGEXES['stakes']), stake)]
            },
            fallbacks=[
                MessageHandler(Filters.text & ~Filters.command, wrong_data),
                CommandHandler('abort', abort)
            ]
        )

        dispatcher.add_handler(conv_handler)
        dispatcher.add_handler(CallbackQueryHandler(button))

        # dispatcher.add_handler(CommandHandler('test', test_message))
        dispatcher.add_handler(CommandHandler('ban', ban))

        are_handlers_set = True


def test_message(update: Update, context: CallbackContext):
    return update.effective_chat.id


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
