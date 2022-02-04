import random

import telegram
from telegram import Update, ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode, InlineKeyboardMarkup, \
    InlineKeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters, PollAnswerHandler, \
    ConversationHandler, CallbackQueryHandler

BOT_TOKEN = "TOKEN"
NGH_CHAT_ID = -1001780891949  # -1001605460175

are_handlers_set = False

updater = Updater(BOT_TOKEN)
dispatcher = updater.dispatcher

LOCATION, DATE, TIME, GAME_FORMAT, ENTRIES_CASH_GAME, ENTRIES_TOURNAMENT, STAKE = range(7)

min_ban_approvers = 5

stakes = ["2€", "5€", "10€", "20€", "50€"]

regexes = dict(
    date="^([1-9]|0[1-9]|1\d|2\d|3[01])\/([1-9]|0[1-9]|1[0-2])\/(((20)\d{2})|(\d{2}))$",
    time="^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$",
    game_formats='^(Cash Game|Torneo)$',
    number_of_cash_game_players="^[2-9]$",
    number_of_tournament_players="^(?:[2-9]|(?:[1-9][0-9])|100)$",
    stakes="^(2€|5€|10€|20€|50€)$",
    register="^(🖐 Iscriviaml!)$"
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
    "Strippacazzi.",
    "Annusaculi.",
    "Bidonaro.",
    "Rimettiti i soldi nel culo, coglione!",
    "Fumacazzi.",
    "Sapevo che il tuo sport era ciucciare i feltrini delle sedie di un' osteria di Leno",
    "Dai amici banniaml!",
    "Sei meno uomo di me.",
    "Sei un bot a pedali.",
    "Hahahahahah pezzo di merda figlio di puttana.",
    "Scrotocefalo.",
    "Rembambit ensiminit da le marijuane.",
    "Tò dit argota de mal? Tò apó dit che gò quater piante de dat embecile, ve a töle no?! Eh casso però figa.",
    "C'è uno sbirro tra di noi..."
]


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
                DATE: [MessageHandler(Filters.regex(regexes['date']), receive_date)],
                TIME: [MessageHandler(Filters.regex(regexes['time']), receive_time)],
                GAME_FORMAT: [MessageHandler(Filters.regex(regexes['game_formats']), game_format)],
                ENTRIES_CASH_GAME: [MessageHandler(Filters.regex(regexes['number_of_cash_game_players']), entries)],
                ENTRIES_TOURNAMENT: [MessageHandler(Filters.regex(regexes['number_of_tournament_players']), entries)],
                STAKE: [MessageHandler(Filters.regex(regexes['stakes']), stake)]
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
    update.message.from_user.id
    update.message.reply_to_message.from_user
    telegram.ChatAction.mro()
    if update.message.reply_to_message == None:
        return


def wrong_data(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👮 Dati non validi",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def ban(update: Update, context: CallbackContext):
    if update.message.chat.type == 'private':
        update.message.reply_text("Puoi utilizzare questo comando solo in un gruppo.")
        return

    if update.message.reply_to_message is None:
        update.message.reply_text("Invia il comando come risposta all'utente che vuoi bannare.")
        return

    chat_admins = context.bot.get_chat_administrators(update.message.chat.id)
    is_bot_admin = False
    for admin in chat_admins:
        if context.bot.id == admin.user.id:
            is_bot_admin = True
            break

    if not is_bot_admin:
        update.message.reply_text("Per utilizzare questo comando devo prima essere promosso ad amministratore del "
                                  "gruppo.")
        return

    caller = update.effective_user
    user_to_ban = update.message.reply_to_message.from_user

    for admin in chat_admins:
        if user_to_ban.id == admin.user.id:
            message = context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"{caller.mention_html()} vuole bannare un amministratore.",
                parse_mode=ParseMode.HTML
            )
            try:
                context.bot.ban_chat_member(
                    chat_id=update.effective_chat.id,
                    user_id=caller.id
                )
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=f"Fai ancora il figo coglione",
                    parse_mode=ParseMode.HTML
                )
            except:
                message.edit_text(
                    text=f"Lol 🐷",
                    parse_mode=ParseMode.HTML
                )
            return

    reason = ""
    if len(context.args) == 0:
        reason = "Nessun motivo"
    else:
        for arg in context.args:
            reason += " " + arg

    while True:
        proposal_id = f"b{random.randint(10000, 99999)}"
        try:
            context.bot_data['ban_proposals'][proposal_id]
        except KeyError:
            break

    payload = {
        "ban_proposals": {
            proposal_id: {
                "caller": caller,
                "user_to_ban": user_to_ban,
                "reason": reason,
                "approvers": list()
            }
        }
    }
    context.bot_data.update(payload)

    keyboard = [[
        InlineKeyboardButton(
            f"👨‍⚖ Ban tro'",
            callback_data=proposal_id
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"{caller.mention_html()} vuola bannare {user_to_ban.mention_html()}."
             f"\nMotivazione: <b>{reason}</b>."
             f"\nApprovazioni: 0 / {min_ban_approvers}",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    return


def new_table0(update: Update, context: CallbackContext):
    if update.message.chat.type != 'private':
        update.message.reply_text("Ti è stato inviato un messaggio in privato.")

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text='🎺 Fai squillare le trombe! 📯'
             '\nInvia il comando /start per iniziare la creazione di un tavolo.'
    )


def start0(update: Update, context: CallbackContext) -> int:
    if update.message.chat.type != 'private':
        return ConversationHandler.END

    while True:
        table_id = random.randint(10000, 99999)
        try:
            context.bot_data[table_id]
        except KeyError:
            break

    context.bot_data.update(dict(last_table_id=table_id))

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text='🎺 Fai squillare le trombe! 📯'
             '\nInvia il comando /abort per annullare.'
    )
    location(update, context)
    return LOCATION


def new_table(update: Update, context: CallbackContext):
    if update.message.chat.type != 'private':
        update.message.reply_text(
            f"Ti è stato inviato un messaggio in <a href=\"tg://user?id={context.bot.id}\">privato</a>.",
            parse_mode=ParseMode.HTML
        )

        context.bot.send_message(
            chat_id=update.effective_user.id,
            text='🎺 Fai squillare le trombe! 📯'
                 '\nInvia il comando /newtable per iniziare la creazione di un tavolo.'
        )
        return ConversationHandler.END

    while True:
        table_id = f"t{random.randint(10000, 99999)}"
        try:
            context.bot_data['tables'][table_id]
        except KeyError:
            break

    payload = {
        "tables": {
            "last_table_id": table_id,
            table_id: {
                "hoster": update.effective_user.mention_html()
            }
        }
    }
    context.bot_data.update(payload)

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text="📍 Dove lo vuoi organizzare?",
        reply_markup=ForceReply(
            force_reply=True,
            selective=True,
            input_field_placeholder="Location dell'evento"
        )
    )
    return LOCATION


def location(update: Update, context: CallbackContext) -> int:
    table_id = context.bot_data['tables']['last_table_id']
    context.bot_data['tables'][table_id].update(dict(
        location=update.message.text
    ))

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text="🗓 Che giorno?"
             "\nRispetta il formato GG/MM/AAAA",
        reply_markup=ForceReply(
            force_reply=True,
            selective=True,
            input_field_placeholder="GG/MM/AAAA"
        )
    )
    return DATE


def receive_date(update: Update, context: CallbackContext) -> int:
    table_id = context.bot_data['tables']['last_table_id']
    context.bot_data['tables'][table_id].update(dict(
        date=update.message.text
    ))

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text="🕒️ Che ora?"
             "\nRispetta il formato HH:MM",
        reply_markup=ForceReply(
            force_reply=True,
            selective=True,
            input_field_placeholder="HH:MM"
        )
    )
    return TIME


def receive_time(update: Update, context: CallbackContext) -> int:
    table_id = context.bot_data['tables']['last_table_id']
    context.bot_data['tables'][table_id].update(dict(
        time=update.message.text
    ))
    reply_keyboard = [['Cash Game', 'Torneo']]

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text="🎲 Che formato vuoi giocare?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
            selective=True,
            input_field_placeholder='Cash Game o torneo?'
        ),
    )

    return GAME_FORMAT


def game_format(update: Update, context: CallbackContext) -> int:
    selected_format = update.message.text

    table_id = context.bot_data['tables']['last_table_id']
    context.bot_data['tables'][table_id].update(dict(
        format=selected_format,
        players=list()
    ))

    message = "👥 Inviami il numero di playerz." \
              "\nScegli un numero compreso tra "
    if selected_format == "Cash Game":
        message += "2 e 9"
        placeholder = "2 - 9"
        return_value = ENTRIES_CASH_GAME
    else:
        message += "2 e 50"
        placeholder = "2 - 50"
        return_value = ENTRIES_TOURNAMENT

    update.message.reply_text(
        message,
        reply_markup=ForceReply(
            force_reply=True,
            selective=True,
            input_field_placeholder=placeholder
        )
    )
    return return_value


def entries(update: Update, context: CallbackContext) -> None:
    table_id = context.bot_data['tables']['last_table_id']
    context.bot_data['tables'][table_id].update(dict(entries_limit=update.message.text))
    reply_keyboard = [stakes]

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
    return STAKE


def stake(update: Update, context: CallbackContext):
    table_id = context.bot_data['tables']['last_table_id']
    table = context.bot_data['tables'][table_id]
    context.bot_data['tables'][table_id].update(dict(
        stake=stakes.index(update.message.text),
        registration_open=True
    ))

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"🎺 <b>ISCRIZIONI APERTE</b> 📯"
             f"\nÈ stato inviato il modulo d' iscrizione sul gruppo della N.G.H.!",
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )

    keyboard = [[
        InlineKeyboardButton(
            f"🖐 Iscriviaml!"
            f"  {len(table['players'])} / {table['entries_limit']}",
            callback_data=table_id
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=NGH_CHAT_ID,
        text=f"\n\nHost: {table['hoster']}"
             f"\n📍 Presso {table['location']}"
             f"\n🗓 il {table['date']} alle {table['time']}"
             f"\n🎲 {table['format']}"
             f"\n👥 {table['entries_limit']} max"
             f"\n💸 {stakes[table['stake']]}"
             f"\n\n🎺 <b>ISCRIZIONI APERTE</b> 📯",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    return ConversationHandler.END


def button(update: Update, context: CallbackContext):
    callback_query_data = update.callback_query.data
    if callback_query_data.startswith("t"):
        table_button(update, context)
    elif callback_query_data.startswith("b"):
        ban_button(update, context)
    else:
        return


def ban_button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    proposal_id = query.data
    try:
        ban_proposal = context.bot_data['ban_proposals'][proposal_id]
    except KeyError:
        query.edit_message_text(
            text=f"<i>proposta di ban scaduta</i>",
            parse_mode=ParseMode.HTML
        )
        return

    approvers_ids = ban_proposal['approvers']
    user_id = update.effective_user.id
    if user_id in approvers_ids:
        return

    approvers_ids.append(user_id)

    keyboard = [[
        InlineKeyboardButton(
            f"👨‍⚖ Ban tro'",
            callback_data=query.data
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    approvers = len(approvers_ids)
    if approvers < min_ban_approvers:
        query.edit_message_text(
            text=f"{ban_proposal['caller'].mention_html()} vuola bannare {ban_proposal['user_to_ban'].mention_html()}."
                 f"\nMotivazione: <b>{ban_proposal['reason']}</b>."
                 f"\nApprovazioni: {approvers} / {min_ban_approvers}",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    else:
        query.edit_message_text(
            text=f"{ban_proposal['caller'].mention_html()} vuola bannare {ban_proposal['user_to_ban'].mention_html()}."
                 f"\nMotivazione: <b>{ban_proposal['reason']}</b>."
                 f"\nApprovazioni: {approvers} / {min_ban_approvers}",
            parse_mode=ParseMode.HTML
        )
        try:
            context.bot.ban_chat_member(
                chat_id=update.effective_chat.id,
                user_id=ban_proposal['user_to_ban'].id
            )
        except:
            query.edit_message_text(
                text=f"<i>qualcosa è andato storto</i>",
                parse_mode=ParseMode.HTML
            )


def table_button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    table_id = query.data
    try:
        table = context.bot_data['tables'][table_id]
    except KeyError:
        query.edit_message_text(
            text=f"<i>tavolo scaduto</i>",
            parse_mode=ParseMode.HTML
        )
        return

    players = table['players']
    user = update.effective_user.mention_html()
    if user in players:
        return

    players.append(user)

    keyboard = [[
        InlineKeyboardButton(
            f"🖐 Iscriviaml!"
            f" {len(players)} / {table['entries_limit']}",
            callback_data=query.data
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    players_list = ""
    for player in table['players']:
        players_list += f"\n>{player}"

    if len(players) < int(table['entries_limit']):
        query.edit_message_text(
            text=f"\n\nHost: {table['hoster']}"
                 f"\n📍 Presso {table['location']}"
                 f"\n🗓 il {table['date']} alle {table['time']}"
                 f"\n🎲 {table['format']}"
                 f"\n👥 {table['entries_limit']} max"
                 f"\n💸 {stakes[table['stake']]}"
                 f"\n\n🎺 <b>ISCRIZIONI APERTE</b> 📯"
                 f"\nPlayers: {players_list}",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    else:
        table['registration_open'] = False
        query.edit_message_text(
            text=f"\n\nHost: {table['hoster']}"
                 f"\n📍 Presso {table['location']}"
                 f"\n🗓 il {table['date']} alle {table['time']}"
                 f"\n🎲 {table['format']}"
                 f"\n👥 {table['entries_limit']} max"
                 f"\n💸 {stakes[table['stake']]}"
                 f"\n\n🚫 <b>ISCRIZIONI CHIUSE</b> 🚫"
                 f"\nPlayers: {players_list}",
            parse_mode=ParseMode.HTML
        )


def abort(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        random.choice(insults),
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


if __name__ == "__main__":
    test()
