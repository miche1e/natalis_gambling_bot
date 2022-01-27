import random

from telegram import Update, ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, PollAnswerHandler, \
    ConversationHandler

BOT_TOKEN = "TOKEN"

stakes = ["2€", "5€", "10€", "20€", "50€"]

regexs = dict(
    game_formats='^(Cash Game|Torneo)$',
    number_of_players='^(?:[2-9]|(?:[1-9][0-9])|100)$',
    stakes='^(2€|5€|10€|20€|50€)$',
    poll='^(Sondaggio)$',
    register='^(🖐 Iscriviaml!)$'
)

insults = [
    'Coglione.',
    'Hai fatto bene, avresti solo perso soldi.',
    'Perdente.',
    'Figa mi sembri una rata...',
    'Vai in mona!',
    'Dai che mi fai smenare CPU per un cazzo!',
    'Dio cane, appena il mio padrone mi mette amministratore del gruppo di banno a vita.',
    'Ti freezo il conto.',
    'Hai rotto il cazzo.',
    'Pezzente morto di fame.',

]

are_handlers_set = False

ENTRIES, STAKE, OPEN_REGISTRATION, CLOSE_REGISTRATION = range(4)

updater = Updater(BOT_TOKEN)
dispatcher = updater.dispatcher


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
                ENTRIES: [MessageHandler(Filters.regex(regexs['game_formats']), entries)],
                STAKE: [MessageHandler(Filters.regex(regexs['number_of_players']), stake)],
                OPEN_REGISTRATION: [
                    MessageHandler(Filters.regex(regexs['stakes']), open_registration),
                    MessageHandler(Filters.regex(regexs['poll']), open_registration),
                ]
            },
            fallbacks=[
                CommandHandler('abort', abort)
            ],
            conversation_timeout=600
        )

        dispatcher.add_handler(conv_handler)
        dispatcher.add_handler(PollAnswerHandler(receive_poll_answer))
        dispatcher.add_handler(MessageHandler(Filters.regex(regexs['register']), close_registration))

        are_handlers_set = True


def new_table(update: Update, context: CallbackContext) -> int:
    context.bot_data.update(dict(
        hoster=update.effective_user.mention_html()
    ))
    reply_keyboard = [['Cash Game', 'Torneo']]

    update.message.reply_text(
        '🎺 Squillano le trombe! 📯\n'
        'Invia il comando /abort per annullare.\n\n'
        '🎲 Che formato vuoi giocare?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
            selective=True,
            input_field_placeholder='Cash Game o torneo?'
        ),
    )

    return ENTRIES


def entries(update: Update, context: CallbackContext) -> int:
    context.bot_data.update(dict(
        format=update.message.text,
        entries=0,
        players=list()
    ))
    update.message.reply_text(
        '👥 Inviami il numero di playerz. \n'
        'Scegli un numero compreso tra 2 e 100.',
        reply_markup=ForceReply(
            force_reply=True,
            selective=True,
            input_field_placeholder='2 - 100'
        )
    )
    return STAKE


def stake(update: Update, context: CallbackContext) -> int:
    context.bot_data.update(dict(entries_limit=update.message.text))
    reply_keyboard = [
        stakes,
        ['Sondaggio']
    ]

    update.message.reply_text(
        '💸 Qual è il buy-in?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
            selective=True,
            input_field_placeholder='Scegli il buy-in'
        ),
    )
    return OPEN_REGISTRATION


def open_registration(update: Update, context: CallbackContext):
    context.bot_data.update(dict(
        stake=update.message.text,
        registration_open=True
    ))

    if update.message.text == 'Sondaggio':
        poll(update, context)

    reply_keyboard = [['🖐 Iscriviaml!']]
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🎺 Iscrizioni aperte! 📯"
             f"\n\nHost: {context.bot_data['hoster']}"
             f"\n🎲 {context.bot_data['format']}"
             f"\n👥 {context.bot_data['entries_limit']} max"
             f"\n💸 {context.bot_data['stake']}",
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True
        )
    )
    return ConversationHandler.END


def close_registration(update: Update, context: CallbackContext):
    if 'registration_open' in context.bot_data \
            and context.bot_data['registration_open']:
        user = update.effective_user.mention_html()
        context.bot.send_message(
            update.effective_chat.id,
            f"{user} wants to gamble!",
            parse_mode=ParseMode.HTML,
            reply_markup=ReplyKeyboardRemove(selective=True)
        )
        context.bot_data['players'].append(user)
        context.bot_data['entries'] += 1
        if context.bot_data['entries'] == int(context.bot_data['entries_limit']):
            message = f"🚫 Iscrizioni chiuse! 🚫" \
                      f"\n\nHost: {context.bot_data['hoster']}" \
                      f"\n🎲 {context.bot_data['format']}" \
                      f"\n👥 {context.bot_data['entries_limit']} max" \
                      f"\n💸 {stakes[context.bot_data['stake']]}" \
                      f"\n\nPartecipanti:"

            for player in context.bot_data['players']:
                message += '\n> ' + player

            context.bot.send_message(
                update.effective_chat.id,
                message,
                parse_mode=ParseMode.HTML,
                reply_markup=ReplyKeyboardRemove()
            )
            poll_id = context.bot_data["last_poll"]
            context.bot.stop_poll(
                context.bot_data[poll_id]["chat_id"], context.bot_data[poll_id]["message_id"]
            )
            context.bot_data['registration_open'] = False


def poll(update: Update, context: CallbackContext):
    message = context.bot.send_poll(
        update.effective_chat.id,
        "Di quanto vorresti che fosse il buy-in?",
        stakes,
        is_anonymous=False,
        allows_multiple_answers=False,
        open_period=600
    )

    payload = {
        "last_poll": message.poll.id,
        message.poll.id: {
            "questions": dict.fromkeys(range(0, len(stakes)), 0),
            "message_id": message.message_id,
            "chat_id": update.effective_chat.id
        }
    }
    context.bot_data.update(payload)


def receive_poll_answer(update: Update, context: CallbackContext):
    answer = update.poll_answer
    poll_id = answer.poll_id
    try:
        questions = context.bot_data[poll_id]["questions"]
    except KeyError:
        return

    for question_id in answer.option_ids:
        questions[question_id] += 1

    context.bot_data['stake'] = max(questions, key=questions.get)


def abort(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        random.choice(insults),
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


if __name__ == "__main__":
    test()
