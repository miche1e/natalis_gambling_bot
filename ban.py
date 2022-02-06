import random

from telegram import ParseMode, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from constants import MIN_BAN_APPROVERS


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
        random_number = random.randint(10000, 99999)
        proposal_id = "B" + str(random_number)
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
             f"\nApprovazioni: 0 / {MIN_BAN_APPROVERS}",
        parse_mode=ParseMode.HTML,
        reply_markup=reply_markup
    )
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
    if approvers < MIN_BAN_APPROVERS:
        query.edit_message_text(
            text=f"{ban_proposal['caller'].mention_html()} vuola bannare {ban_proposal['user_to_ban'].mention_html()}."
                 f"\nMotivazione: <b>{ban_proposal['reason']}</b>."
                 f"\nApprovazioni: {approvers} / {MIN_BAN_APPROVERS}",
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    else:
        query.edit_message_text(
            text=f"{ban_proposal['caller'].mention_html()} vuola bannare {ban_proposal['user_to_ban'].mention_html()}."
                 f"\nMotivazione: <b>{ban_proposal['reason']}</b>."
                 f"\nApprovazioni: {approvers} / {MIN_BAN_APPROVERS}",
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
