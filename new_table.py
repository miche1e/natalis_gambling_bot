import random
import time

from telegram import Update, ParseMode, ForceReply, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, \
    InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler

from config import CHAT_ID
from constants import LOCATION, DATE, TIME, GAME_FORMAT, ENTRIES_TOURNAMENT, ENTRIES_CASH_GAME, STAKES_BUTTONS, \
    STAKE, TABLE_ID_PREFIX, GAME_FORMATS_BUTTONS, OPEN_REGISTRATION, REGISTER, REGISTRATION_OPTIONS_BUTTONS, \
    OPEN_REGISTRATION_BUTTONS, PERSISTENCE_DAYS, IDS_RANGE
from strings import ngb_newtable_invalidData, ngb_newtable_goToPrivateMessage, ngb_newtable_privateMessage, \
    ngb_newtable_locationText, ngb_newtable_locationPlaceholder, \
    ngb_newtable_dateText, ngb_newtable_datePlaceholder, ngb_newtable_timeText, ngb_newtable_timePlaceholder, \
    ngb_newtable_formatText, ngb_newtable_formatPlaceholder, ngb_newtable_playersText, \
    ngb_newtable_playersNumberTexts, ngb_newtable_playersNumberPlaceholders, ngb_newtable_buyInText, \
    ngb_newtable_buyInPlaceholder, ngb_newtable_openRegistration, \
    ngb_newtable_registrationButton, ngb_newtable_registrationRecap, ngb_newtable_tableExpired, \
    ngb_newtable_listBulletPoint, ngb_newtable_playersLable, \
    ngb_newtable_registrationOpenLabel, ngb_newtable_registrationClosedLabel, ngb_newtable_abortInsults, \
    ngb_newtable_registrationPlaceholder, ngb_newtable_recapTitle, ngb_newtable_registrationMessage, ngb_newtable_abort, \
    ngb_newtable_nullRevoke, ngb_rewtable_revokeTableNotFound, ngb_newtable_revokeRegistrationInfo


def wrong_data(update: Update, _: CallbackContext):
    update.message.reply_text(
        text=ngb_newtable_invalidData,
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def revoke_registration(update: Update, context: CallbackContext):
    message = update.message.reply_to_message
    if message is None:
        update.message.reply_text(text=ngb_newtable_nullRevoke)
        return

    try:
        table_id = context.bot_data['message_table_associations_dictionary'][message.message_id]
        table = context.bot_data['tables'][table_id]
        players_list = context.bot_data['tables'][table_id]['players']
    except KeyError:
        update.message.reply_text(text=ngb_rewtable_revokeTableNotFound)
        return

    players_list.remove(update.effective_user.mention_html())

    keyboard = [[
        InlineKeyboardButton(
            text=ngb_newtable_registrationButton.format(len(table['players']), table['entries_limit']),
            callback_data=table_id
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    players_recap = ""
    if len(table['players']) > 0:
        players_list = ""
        for player in table['players']:
            players_list += ngb_newtable_listBulletPoint.format(player)
        players_recap = ngb_newtable_playersLable.format(players_list)
    context.bot.edit_message_text(
        chat_id=CHAT_ID,
        message_id=message.message_id,
        text=ngb_newtable_registrationRecap.format(
            table['hoster'],
            table['location'],
            table['date'],
            table['time'],
            table['format'],
            table['entries_limit'],
            table['stake'],
            ngb_newtable_registrationOpenLabel,
            players_recap,
            ngb_newtable_revokeRegistrationInfo
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )


def new_table(update: Update, context: CallbackContext):
    if update.message.chat.type != 'private':
        try:
            context.bot.send_message(
                chat_id=update.effective_user.id,
                text=ngb_newtable_privateMessage
            )
        except:
            pass

        update.message.reply_text(
            text=ngb_newtable_goToPrivateMessage.format(context.bot.id),
            parse_mode=ParseMode.HTML
        )
        return ConversationHandler.END

    while True:
        random_number = random.randint(*IDS_RANGE)
        table_id = TABLE_ID_PREFIX + str(random_number)
        try:
            random_table = context.bot_data['tables'][table_id]
            if time.time() - random_table['timestamp'] > PERSISTENCE_DAYS * 24 * 60 * 60:
                break
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
        text=ngb_newtable_abort
    )

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=ngb_newtable_locationText,
        reply_markup=ForceReply(
            force_reply=True,
            selective=True,
            input_field_placeholder=ngb_newtable_locationPlaceholder
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
        text=ngb_newtable_dateText,
        reply_markup=ForceReply(
            force_reply=True,
            selective=True,
            input_field_placeholder=ngb_newtable_datePlaceholder
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
        text=ngb_newtable_timeText,
        reply_markup=ForceReply(
            force_reply=True,
            selective=True,
            input_field_placeholder=ngb_newtable_timePlaceholder
        )
    )
    return TIME


def receive_time(update: Update, context: CallbackContext) -> int:
    table_id = context.chat_data['last_table_id']
    context.bot_data['tables'][table_id].update(dict(
        time=update.message.text
    ))
    reply_keyboard = [GAME_FORMATS_BUTTONS]

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=ngb_newtable_formatText,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
            selective=True,
            input_field_placeholder=ngb_newtable_formatPlaceholder
        ),
    )

    return GAME_FORMAT


def game_format(update: Update, context: CallbackContext) -> int:
    selected_format = update.message.text

    table_id = context.chat_data['last_table_id']
    context.bot_data['tables'][table_id].update(dict(
        format=selected_format
    ))

    message = ngb_newtable_playersText
    if selected_format == GAME_FORMATS_BUTTONS[0]:
        message += ngb_newtable_playersNumberTexts[0]
        placeholder = ngb_newtable_playersNumberPlaceholders[0]
        return_value = ENTRIES_CASH_GAME
    else:
        message += ngb_newtable_playersNumberTexts[1]
        placeholder = ngb_newtable_playersNumberPlaceholders[1]
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


def entries(update: Update, context: CallbackContext) -> int:
    table_id = context.chat_data['last_table_id']
    context.bot_data['tables'][table_id].update(dict(entries_limit=update.message.text))
    reply_keyboard = [STAKES_BUTTONS]

    update.message.reply_text(
        text=ngb_newtable_buyInText,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
            selective=True,
            input_field_placeholder=ngb_newtable_buyInPlaceholder
        ),
    )
    return STAKE


def stake(update: Update, context: CallbackContext) -> int:
    table_id = context.chat_data['last_table_id']
    context.bot_data['tables'][table_id].update(dict(
        stake=update.message.text
    ))

    reply_keyboard = [REGISTRATION_OPTIONS_BUTTONS]
    update.message.reply_text(
        text=ngb_newtable_registrationMessage,
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            resize_keyboard=True,
            selective=True,
            input_field_placeholder=ngb_newtable_registrationPlaceholder
        ),
    )
    return REGISTER


def register(update: Update, context: CallbackContext) -> int:
    table_id = context.chat_data['last_table_id']
    table = context.bot_data['tables'][table_id]
    table.update(dict(players=list()))
    if update.message.text == REGISTRATION_OPTIONS_BUTTONS[0]:
        table['players'].append(update.effective_user.mention_html())

    keyboard = [OPEN_REGISTRATION_BUTTONS]
    reply_markup = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
        selective=True
    )

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=ngb_newtable_recapTitle + ngb_newtable_registrationRecap.format(
            table['hoster'],
            table['location'],
            table['date'],
            table['time'],
            table['format'],
            table['entries_limit'],
            table['stake'],
            "", "", ""
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

    return OPEN_REGISTRATION


def open_registration(update: Update, context: CallbackContext):
    table_id = context.chat_data['last_table_id']
    table = context.bot_data['tables'][table_id]
    table.update(dict(
        registration_open=True,
        timestamp=time.time()
    ))

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=ngb_newtable_openRegistration,
        parse_mode=ParseMode.HTML,
        reply_markup=ReplyKeyboardRemove()
    )

    keyboard = [[
        InlineKeyboardButton(
            text=ngb_newtable_registrationButton.format(len(table['players']), table['entries_limit']),
            callback_data=table_id
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    players_recap = ""
    if len(table['players']) > 0:
        players_list = ""
        for player in table['players']:
            players_list += ngb_newtable_listBulletPoint.format(player)
        players_recap = ngb_newtable_playersLable.format(players_list)

    message = context.bot.send_message(
        chat_id=CHAT_ID,
        text=ngb_newtable_registrationRecap.format(
            table['hoster'],
            table['location'],
            table['date'],
            table['time'],
            table['format'],
            table['entries_limit'],
            table['stake'],
            ngb_newtable_registrationOpenLabel,
            players_recap,
            ngb_newtable_revokeRegistrationInfo
        ),
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )

    message_table_association = {message.message_id: table_id}

    try:
        message_table_association_dictionary = context.bot_data['message_table_associations_dictionary']
    except KeyError:
        context.bot_data.update(dict(
            message_table_associations_dictionary=dict()
        ))
        message_table_association_dictionary = context.bot_data['message_table_associations_dictionary']

    context.bot_data['message_table_associations_dictionary'].update(message_table_association)
    return ConversationHandler.END


def table_button(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    table_id = query.data
    try:
        table = context.bot_data['tables'][table_id]
    except KeyError:
        query.edit_message_text(
            text=ngb_newtable_tableExpired,
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
            text=ngb_newtable_registrationButton.format(len(table['players']), table['entries_limit']),
            callback_data=query.data
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    players_list = ""
    for player in table['players']:
        players_list += ngb_newtable_listBulletPoint.format(player)

    if len(players) < int(table['entries_limit']):
        query.edit_message_text(
            text=ngb_newtable_registrationRecap.format(
                table['hoster'],
                table['location'],
                table['date'],
                table['time'],
                table['format'],
                table['entries_limit'],
                table['stake'],
                ngb_newtable_registrationOpenLabel,
                ngb_newtable_playersLable.format(players_list),
                ngb_newtable_revokeRegistrationInfo
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    else:
        table['registration_open'] = False
        query.edit_message_text(
            text=ngb_newtable_registrationRecap.format(
                table['hoster'],
                table['location'],
                table['date'],
                table['time'],
                table['format'],
                table['entries_limit'],
                table['stake'],
                ngb_newtable_registrationClosedLabel,
                ngb_newtable_playersLable.format(players_list),
                ngb_newtable_revokeRegistrationInfo
            ),
            parse_mode=ParseMode.HTML
        )


def abort(update: Update, _: CallbackContext) -> int:
    update.message.reply_text(
        random.choice(ngb_newtable_abortInsults),
        reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END
