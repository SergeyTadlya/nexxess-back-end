from django.core.mail import send_mail
from django.db.models import Q

from .keyboards import *
from ..utils import *
from ..system_commands import *
from ...models import Authentication, User

from random import randint
import logging


logger = logging.getLogger(__name__)


class StartHandler:
    def __init__(self, bot, data):
        self.bot = bot
        self.data = data

    @staticmethod
    def message_validation(user_message, bot, data):
        if 'text' in user_message.keys():
            if user_message['text'] == '/start':
                StartHandler.start(bot, data)
                return

            if '/' not in user_message['text']:
                message = user_message['text'].strip()
                return message
            else:
                bot.sendMessage(chat_id=get_chat_id(data),
                                text='Try writing a message without the "/":\n')
                return None
        else:
            bot.sendMessage(chat_id=get_chat_id(data),
                            text='This is not a text format\n'
                                 'Try to write something similar to the text:')
            return None

    @staticmethod
    def main_keyboard():
        return main_keyboard()

    @staticmethod
    def show_menu(bot, data):
        set_up_commands(bot)
        bot.sendMessage(chat_id=get_chat_id(data),
                        text='Something info here about bot',
                        reply_markup=main_keyboard())

    @staticmethod
    def start(bot, data):
        user = get_user(data)
        if isinstance(user, User):
            message = 'Authorization was successful.\n' \
                      'Now you can use commands or keyboard for more comfortable'

            bot.sendMessage(chat_id=get_chat_id(data),
                            text=message,
                            reply_markup=main_keyboard())

        elif isinstance(user, Authentication):
            bot.sendMessage(chat_id=get_chat_id(data),
                            text='Please, authorize first!\n'
                                 'Type your email or username 👇')
        else:
            bot.sendMessage(chat_id=get_chat_id(data),
                            text='User not authorize and not in db')


class AuthenticationHandler:
    def __init__(self, bot, data):
        self.bot = bot
        self.data = data

    def set_user_email(self, data):
        email_or_username = StartHandler.message_validation(data['message'], self.bot, self.data)
        if email_or_username is None:
            return

        user = User.objects.filter(Q(email=email_or_username) | Q(username=email_or_username))

        if user.exists():
            user = user.first()
            if user.telegram_is_authenticate:
                self.bot.sendMessage(chat_id=get_chat_id(data),
                                     text='It seems that the user is already authenticated in Telegram')
        else:
            self.bot.sendMessage(chat_id=get_chat_id(data),
                                 text='The user with this email does not exist on the site.\n'
                                      'Log in first on the site to use the Telegram bot.\n\n'
                                      'Here is a link to our site:\n'
                                      'https://dev1.nexxess.com/')
            return

        unauthorized_user = Authentication.objects.filter(telegram_id=self.data['message']['from']['id'])
        if unauthorized_user.exists():
            unauthorized_user = unauthorized_user.first()

        try:
            code = randint(100000, 999999)
            unauthorized_user.verify_code = code
            unauthorized_user.email = user.email
            unauthorized_user.step = 'SET_VERIFY_CODE'
            unauthorized_user.save()

            self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                 text=f'Greate!\n'
                                      f'(if you want to write another email, click -> /start).\n'
                                      f'We have sent a confirmation code to the {unauthorized_user.email}\n'
                                      f'Check it and write here your code:')
            send_mail('Secret key',
                      f'Your private key for {unauthorized_user.email}:\n\n{code}',
                      'info@nexxess.com',
                      [unauthorized_user.email],
                      fail_silently=False)
        except Exception as e:
            # Exception logger credentials
            user_chat_id = self.data['message']['from']['id']
            username = self.data['message']['from']['username']

            logger.error(f'Exception: {username} ({user_chat_id}) - {e}')

    def set_user_verification_code(self, data):
        unauthorized_user = Authentication.objects.filter(telegram_id=self.data['message']['from']['id'])
        if unauthorized_user.exists():
            unauthorized_user = unauthorized_user.first()

        verify_code = StartHandler.message_validation(data['message'], self.bot, self.data)
        self.bot.deleteMessage(message_id=self.data['message']['message_id'],
                               chat_id=get_chat_id(self.data))
        if verify_code is None:
            return

        if verify_code == unauthorized_user.verify_code:
            unauthorized_user.step = ''
            unauthorized_user.save()

            authorize_user(data['message'])
            set_up_commands(self.bot)

            self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                 text='Awesome! 😎\n\n'
                                      'Authorization was successful.\n'
                                      'Familiarize yourself with this information below 👇')
            StartHandler.show_menu(self.bot, self.data)
        else:
            self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                 text='🤔 Hmmm...\n'
                                      'The verification code is not valid, please check it and try one more time 👇')
