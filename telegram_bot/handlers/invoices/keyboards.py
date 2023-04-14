from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def there_are_invoices_keyboard() -> InlineKeyboardMarkup:
    pass


def has_no_invoices_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('View history', callback_data='invoices_history')]
    ]
    return InlineKeyboardMarkup(buttons)


def types_invoices_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('Paid', callback_data='invoices_paid'),
         InlineKeyboardButton('Unpaid', callback_data='invoices_unpaid')],
        [InlineKeyboardButton('Canceled', callback_data='invoices_canceled'),
         InlineKeyboardButton('Refunded', callback_data='invoices_refunded')]
    ]
    return InlineKeyboardMarkup(buttons)
