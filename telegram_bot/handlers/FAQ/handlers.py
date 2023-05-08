from .keyboards import *
from ..utils import *


class FAQHandler:
    def __init__(self, bot, data):
        self.bot = bot
        self.data = data

    @staticmethod
    def show_faq_menu(bot, data):
        bot.sendMessage(chat_id=get_chat_id(data),
                        text='Choose the topic for more information',
                        reply_markup=faqs_topics_keyboard())
