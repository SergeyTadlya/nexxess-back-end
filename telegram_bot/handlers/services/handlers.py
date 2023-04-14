from .keyboards import *
from ..utils import *


class ServicesHandler:
    def __init__(self, bot, data):
        self.bot = bot
        self.data = data

    @staticmethod
    def show_keyboard(bot, data):
        bot.sendMessage(chat_id=get_chat_id(data),
                        text='Choose the option',
                        reply_markup=services_keyboard())
