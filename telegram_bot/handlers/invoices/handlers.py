from .keyboards import *
from ..utils import *


class InvoiceHandler:
    def __init__(self, bot, data, callback_title):
        self.bot = bot
        self.data = data

        callback_title = str(callback_title).replace('invoices_', '')

        if callback_title == 'history':
            self.show_type_invoices()

    @staticmethod
    def show_keyboard(bot, data):
        invoices = ''
        if not invoices == '':
            pass
        else:
            bot.sendMessage(chat_id=get_chat_id(data),
                            text='You have no new invoices',
                            reply_markup=has_no_invoices_keyboard())

    def show_type_invoices(self):
        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text='Choose the type of invoices',
                             reply_markup=types_invoices_keyboard())
