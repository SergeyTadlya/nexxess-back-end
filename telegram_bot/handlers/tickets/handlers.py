from .keyboards import *
from ..utils import *


class TicketsHandler:
    def __init__(self, bot, data):
        self.bot = bot
        self.data = data

    @staticmethod
    def show_keyboard(bot, data):
        tickets = ''
        if not tickets == '':
            pass
        else:
            bot.sendMessage(chat_id=get_chat_id(data),
                            text='You have no tickets',
                            reply_markup=has_no_tickets())
