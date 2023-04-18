from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def there_are_tickets() -> InlineKeyboardMarkup:
    pass


def has_no_tickets() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('All ticket', callback_data='tickets_all')],
        [InlineKeyboardButton('Create new', callback_data='tickets_new')]
    ]
    return InlineKeyboardMarkup(buttons)
