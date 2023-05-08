from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def tickets_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('My tickets', callback_data='tickets_my')],
        [InlineKeyboardButton('Create ticket', callback_data='tickets_create')]
    ]

    return InlineKeyboardMarkup(buttons)
