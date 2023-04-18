from .keyboards import *
from ..utils import *
from ..system_commands import *
from ...models import Authentication, User


class StartHandler:
    def __init__(self, bot, data):
        self.bot = bot
        self.data = data

    @staticmethod
    def main_keyboard():
        return main_keyboard()

    @staticmethod
    def show_menu(bot, data):
        bot.sendMessage(chat_id=get_chat_id(data), text='Menu')

    @staticmethod
    def start(bot, data):
        user = get_user(data)
        if user is not None:
            message = 'Account ID: ' + str(user.telegram_id) + '\n' + \
                      'Date created: ' + str(user.date_joined)[:10] + ' ' + str(user.date_joined)[11:16] + '\n\n'

            bot.sendMessage(chat_id=get_chat_id(data),
                            text=message,
                            reply_markup=main_keyboard())

        else:
            bot.sendMessage(chat_id=get_chat_id(data),
                            text='Please, authorize first!\n\nType your email or username 👇')


class AuthenticationHandler:
    def __init__(self, bot, data):
        self.bot = bot
        self.data = data

    def set_user_email(self, data):
        email = data['message']['text']
        if User.objects.filter(email=email):
            self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                 text='Oops...\nThis email already exists, try another one:')

            return
        if email.count('@') == 1:
            unauthorized_user = Authentication.objects.filter(telegram_id=self.data['message']['from']['id'])
            if unauthorized_user.exists():
                unauthorized_user = unauthorized_user.first()
            unauthorized_user.email = email
            unauthorized_user.step = 'set_password'
            unauthorized_user.save()

            self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                 text='Greate! 🤗\nAnd now type your password. \nPlease, do not show it to others! 🤫')
        else:
            self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                 text='🤔 Hmmm... \nSomething wrong: please, check it and try one more time 👇')

    def set_user_password(self, data):
        unauthorized_user = Authentication.objects.filter(telegram_id=self.data['message']['from']['id'])
        if unauthorized_user.exists():
            unauthorized_user = unauthorized_user.first()

        password = data['message']['text'].strip()
        self.bot.deleteMessage(message_id=self.data['message']['message_id'],
                               chat_id=get_chat_id(self.data))
        if len(password) > 8:
            unauthorized_user.password = password
            unauthorized_user.save()

            authorize_user(data['message'])

            set_up_commands(self.bot)

            self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                 text='Awesome!😎 \n\n'
                                      'Now check up your email and enter the code we sent for verification 👇')
        else:
            self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                 text='🤔 Hmmm... \nSomething wrong: please, check it and try one more time 👇')
