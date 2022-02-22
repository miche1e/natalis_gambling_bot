import random
import time

from telegram import ParseMode, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from constants import MIN_BAN_APPROVERS, BAN_PROPOSAL_ID_PREFIX, PERSISTENCE_DAYS, IDS_RANGE
from strings import ngb_ban_groupChatWarn, ngb_ban_instruction, ngb_ban_adminPromotion, ngb_ban_adminBanAttemptText, \
    ngb_ban_adminBanAdminAttempt, ngb_ban_adminBanAttemptInsult, ngb_ban_noReason, ngb_ban_button, ngb_ban_recapMessage, \
    ngb_ban_proposalExpired, ngb_ban_somethingWentWrong


def ban(update: Update, context: CallbackContext):
    if update.message.chat.type == 'private':
        update.message.reply_text(ngb_ban_groupChatWarn)
        return

    if update.message.reply_to_message is None:
        update.message.reply_text(ngb_ban_instruction)
        return

    chat_admins = context.bot.get_chat_administrators(update.message.chat.id)
    is_bot_admin = False
    for admin in chat_admins:
        if context.bot.id == admin.user.id:
            is_bot_admin = True
            break

    if not is_bot_admin:
        update.message.reply_text(ngb_ban_adminPromotion)
        return

    caller = update.effective_user
    user_to_ban = update.message.reply_to_message.from_user

    for admin in chat_admins:
        if user_to_ban.id == admin.user.id:
            message = context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=ngb_ban_adminBanAttemptText.format(caller.mention_html()),
                parse_mode=ParseMode.HTML
            )
            try:
                context.bot.ban_chat_member(
                    chat_id=update.effective_chat.id,
                    user_id=caller.id
                )
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text=ngb_ban_adminBanAttemptInsult,
                    parse_mode=ParseMode.HTML
                )
            except:
                message.edit_text(
                    text=ngb_ban_adminBanAdminAttempt,
                    parse_mode=ParseMode.HTML
                )
            return

    reason = ""
    if len(context.args) == 0:
        reason = ngb_ban_noReason
    else:
        for arg in context.args:
            reason += " " + arg

    try:
        ban_proposals = context.bot_data['ban_proposals']
    except KeyError:
        context.bot_data.update(dict(
            ban_proposals=dict()
        ))
        ban_proposals = context.bot_data['ban_proposals']

    while True:
        random_number = random.randint(*IDS_RANGE)
        proposal_id = BAN_PROPOSAL_ID_PREFIX + str(random_number)
        try:
            ban_proposal = ban_proposals[proposal_id]
            if time.time() - ban_proposal['timestamp'] > PERSISTENCE_DAYS * 24 * 60 * 60:
                break
        except KeyError:
            break

    payload = {
        proposal_id: {
            "caller": caller,
            "user_to_ban": user_to_ban,
            "reason": reason,
            "approvers": list(),
            "timestamp": time.time()
        }
    }

    ban_proposals.update(payload)

    keyboard = [[
        InlineKeyboardButton(
            text=ngb_ban_button,
            callback_data=proposal_id
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    approvers = len(context.bot_data['ban_proposals'][proposal_id]['approvers'])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=ngb_ban_recapMessage.format(
            caller.mention_html(),
            user_to_ban.mention_html(),
            reason,
            approvers,
            MIN_BAN_APPROVERS
        ),
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
            text=ngb_ban_proposalExpired,
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
            text=ngb_ban_button,
            callback_data=query.data
        )
    ]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    approvers = len(approvers_ids)
    if approvers < MIN_BAN_APPROVERS:
        query.edit_message_text(
            text=ngb_ban_recapMessage.format(
                ban_proposal['caller'].mention_html(),
                ban_proposal['user_to_ban'].mention_html(),
                ban_proposal['reason'],
                approvers,
                MIN_BAN_APPROVERS
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    else:
        query.edit_message_text(
            text=ngb_ban_recapMessage.format(
                ban_proposal['caller'].mention_html(),
                ban_proposal['user_to_ban'].mention_html(),
                ban_proposal['reason'],
                approvers,
                MIN_BAN_APPROVERS
            ),
            parse_mode=ParseMode.HTML
        )
        try:
            context.bot.ban_chat_member(
                chat_id=update.effective_chat.id,
                user_id=ban_proposal['user_to_ban'].id
            )
        except:
            query.edit_message_text(
                text=ngb_ban_somethingWentWrong,
                parse_mode=ParseMode.HTML
            )
