from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def services_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('My service', callback_data='services_my')],
        [InlineKeyboardButton('All services', callback_data='services_all')]
    ]
    return InlineKeyboardMarkup(buttons)
