import os

from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, \
    ConversationHandler, CallbackQueryHandler, PicklePersistence

from ban import ban_button, ban
from config import TOKEN, PORT, DOMAIN, USE_WEBHOOK
from constants import LOCATION, DATE, TIME, GAME_FORMAT, ENTRIES_CASH_GAME, ENTRIES_TOURNAMENT, STAKE, \
    REGEXES, TABLE_ID_PREFIX, BAN_PROPOSAL_ID_PREFIX, REGISTER, OPEN_REGISTRATION
from new_table import location, receive_date, receive_time, game_format, entries, stake, abort, new_table, wrong_data, \
    table_button, register, open_registration, revoke_registration
from strings import ngb_main_startMessage, ngb_main_help

persistence = PicklePersistence(filename='database')
updater = Updater(TOKEN, persistence=persistence, use_context=True)
dispatcher = updater.dispatcher

are_handlers_set = False


def main() -> None:
    set_handlers()
    if USE_WEBHOOK:
        start_webhook()
    else:
        start_polling()
    updater.idle()


def start_polling() -> None:
    updater.start_polling()


def start_webhook() -> None:
    port = int(os.environ.get('PORT', PORT))
    updater.start_webhook(listen="0.0.0.0",
                          port=port,
                          url_path=TOKEN,
                          webhook_url=f"https://{DOMAIN}:{PORT}/{TOKEN}")


def entry_point(request):
    if request.method == "POST":
        set_handlers()
        update = Update.de_json(request.get_json(force=True), updater.bot)
        dispatcher.process_update(update)
    return "ok"


def set_handlers():
    global are_handlers_set
    if not are_handlers_set:
        dispatcher.add_handler(CommandHandler('start', start))
        dispatcher.add_handler(CommandHandler('help', help_command))
        dispatcher.add_handler(CommandHandler('ban', ban))
        dispatcher.add_handler(CommandHandler('revoke', revoke_registration))
        # dispatcher.add_handler(CommandHandler('test', test_message))

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


def test_message(update: Update, _: CallbackContext):
    return update.effective_chat.id


def start(update: Update, context: CallbackContext):
    if update.message.chat.type != 'private':
        return

    update.message.reply_text(
        text=ngb_main_startMessage
    )


def help_command(update: Update, context: CallbackContext):
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
    main()
