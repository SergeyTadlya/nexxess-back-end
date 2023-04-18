from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def confirm_logout() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('👍 Yes', callback_data='logout_Yes'),
         InlineKeyboardButton('👎 No', callback_data='logout_No')]
    ]

    return InlineKeyboardMarkup(buttons)
