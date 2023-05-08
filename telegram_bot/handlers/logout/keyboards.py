from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove


def confirm_logout_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('👍 Yes', callback_data='logout_Yes'),
         InlineKeyboardButton('👎 No', callback_data='logout_No')]
    ]

    return InlineKeyboardMarkup(buttons)


def remove_reply_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove(remove_keyboard=True)
