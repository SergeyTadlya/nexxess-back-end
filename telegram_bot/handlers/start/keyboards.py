from telegram import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(text='🧾 Invoices'),
             KeyboardButton(text='👨‍💻 Services')],
            [KeyboardButton(text='📝 Tickets'),
             KeyboardButton(text='⁉️ FAQ')],
            [KeyboardButton(text='🚪 Log Out')]
        ],
        resize_keyboard=True
    )
