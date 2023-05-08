from .keyboards import *
from ..utils import *


class TicketsHandler:
    def __init__(self, bot, data, callback_title):
        self.bot = bot
        self.data = data

        callback_title = callback_title.replace('tickets_', '')

        if callback_title == '':
            pass

    @staticmethod
    def show_tickets_menu(bot, data):
        bot.sendMessage(chat_id=get_chat_id(data),
                        text='Choose options',
                        reply_markup=tickets_menu_keyboard())
