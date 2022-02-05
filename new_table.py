import random

from telegram import Update, ParseMode, ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from constants import LOCATION, DATE, TIME, GAME_FORMAT, ENTRIES_TOURNAMENT, ENTRIES_CASH_GAME, STAKES, INSULTS, \
    NGH_CHAT_ID, STAKE, TABLE_ID_PREFIX, GAME_FORMATS
from strings import invalid_data, go_to_private_chat_message, private_message, location_text, location_placeholder, \
    date_text, date_placeholder, time_text, time_placeholder, format_text, format_placeholder, players_text, \
    number_of_players_text, number_of_players_placeholder, buy_in_text, buy_in_placeholder, open_registration, \
    registration_button, registration_recap_start, table_expired, players_list_bullet_point, players_title, \
    registration_open_label, registration_closed_label


def wrong_data(update: Update, context: CallbackContext):
    update.message.reply_text(
        text=invalid_data,
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def new_table(update: Update, context: CallbackContext):
    if update.message.chat.type != 'private':
        update.message.reply_text(
            text=go_to_private_chat_message.format(context.bot.id),
            parse_mode=ParseMode.HTML
        )

        context.bot.send_message(
            chat_id=update.effective_user.id,
            text=private_message
        )
        return ConversationHandler.END

    while True:
        random_number = random.randint(10000, 99999)
        table_id = TABLE_ID_PREFIX + str(random_number)
        try:
            context.bot_data['tables'][table_id]
        except KeyError:
            break

    context.chat_data.update(dict(
        last_table_id=table_id
    ))

    try:
        tables = context.bot_data['tables']
    except KeyError:
        context.bot_data.update(dict(
            tables=dict()
        ))
        tables = context.bot_data['tables']

    payload = {
        table_id: {
            "hoster": update.effective_user.mention_html()
        }
    }

    tables.update(payload)

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=location_text,
        reply_markup=ForceReply(
            force_reply=True,
            selective=True,
            input_field_placeholder=location_placeholder
        )
    )
    return LOCATION


def location(update: Update, context: CallbackContext) -> int:
    table_id = context.chat_data['last_table_id']
    context.bot_data['tables'][table_id].update(dict(
        location=update.message.text
    ))

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=date_text,
        reply_markup=ForceReply(
            force_reply=True,
            selective=True,
            input_field_placeholder=date_placeholder
        )
    )
    return DATE


def receive_date(update: Update, context: CallbackContext) -> int:
    table_id = context.chat_data['last_table_id']
    context.bot_data['tables'][table_id].update(dict(
        date=update.message.text
    ))

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=time_text,
        reply_markup=ForceReply(
            force_reply=True,
            selective=True,
            input_field_placeholder=time_placeholder
        )
    )
    return TIME


def receive_time(update: Update, context: CallbackContext) -> int:
    table_id = context.chat_data['last_table_id']
    context.bot_data['tables'][table_id].update(dict(
        time=update.message.text
    ))
    reply_keyboard = [GAME_FORMATS]

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=format_text,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
            selective=True,
            input_field_placeholder=format_placeholder
        ),
    )

    return GAME_FORMAT


def game_format(update: Update, context: CallbackContext) -> int:
    selected_format = update.message.text

    table_id = context.chat_data['last_table_id']
    context.bot_data['tables'][table_id].update(dict(
        format=selected_format,
        players=list()
    ))

    message = players_text
    if selected_format == GAME_FORMATS[0]:
        message += number_of_players_text[0]
        placeholder = number_of_players_placeholder[0]
        return_value = ENTRIES_CASH_GAME
    else:
        message += number_of_players_text[1]
        placeholder = number_of_players_placeholder[1]
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
    table_id = context.chat_data['last_table_id']
    context.bot_data['tables'][table_id].update(dict(entries_limit=update.message.text))
    reply_keyboard = [STAKES]

    update.message.reply_text(
        text=buy_in_text,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
            selective=True,
            input_field_placeholder=buy_in_placeholder
        ),
    )
    return STAKE


def stake(update: Update, context: CallbackContext):
    table_id = context.chat_data['last_table_id']
    table = context.bot_data['tables'][table_id]
    context.bot_data['tables'][table_id].update(dict(
        stake=update.message.text,
        registration_open=True
    ))

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=open_registration,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )

    keyboard = [[
        InlineKeyboardButton(
            text=registration_button.format(len(table['players']), table['entries_limit']),
            callback_data=table_id
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=NGH_CHAT_ID,
        text=registration_recap_start.format(
            table['hoster'],
            table['location'],
            table['date'],
            table['time'],
            table['format'],
            table['entries_limit'],
            table['stake']
        ) + registration_open_label,
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
    return ConversationHandler.END


def table_button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    table_id = query.data
    try:
        table = context.bot_data['tables'][table_id]
    except KeyError:
        query.edit_message_text(
            text=table_expired,
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
            text=registration_button.format(len(table['players']), table['entries_limit']),
            callback_data=query.data
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    players_list = ""
    for player in table['players']:
        players_list += players_list_bullet_point.format(player)

    if len(players) < int(table['entries_limit']):
        query.edit_message_text(
            text=registration_recap_start.format(
                table['hoster'],
                table['location'],
                table['date'],
                table['time'],
                table['format'],
                table['entries_limit'],
                table['stake']
            ) + registration_open_label + players_title.format(players_list),
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    else:
        table['registration_open'] = False
        query.edit_message_text(
            text=registration_recap_start.format(
                table['hoster'],
                table['location'],
                table['date'],
                table['time'],
                table['format'],
                table['entries_limit'],
                table['stake']
            ) + registration_closed_label + players_title.format(players_list),
            parse_mode=ParseMode.HTML
        )


def abort(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        random.choice(INSULTS),
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END
