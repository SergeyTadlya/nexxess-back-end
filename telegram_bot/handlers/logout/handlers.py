from .keyboards import *
from ..utils import *
from ..system_commands import *
from ...models import User


class LogOutHandler:
    def __init__(self, bot, data, callback_title):
        self.bot = bot
        self.data = data

        callback_title = str(callback_title).replace('logout_', '')

        if callback_title == 'Yes':
            self.exit()
        elif callback_title == 'No':
            self.delete_confirm_message()

    @staticmethod
    def show_confirm_keyboard(bot, data):
        bot.sendMessage(chat_id=get_chat_id(data),
                        text='Are you sure you want to exit?',
                        reply_markup=confirm_logout())

    def exit(self):
        user = User.objects.filter(telegram_id=self.data['callback_query']['from']['id'])
        if user.exists():
            user = user.first()

        user.telegram_is_authenticate = False
        user.save()

        delete_commands(self.bot)
        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text='You are logged out')

    def delete_confirm_message(self):
        self.bot.deleteMessage(message_id=self.data['callback_query']['message']['message_id'],
                               chat_id=get_chat_id(self.data['callback_query']))
