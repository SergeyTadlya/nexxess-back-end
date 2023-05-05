from .start.handlers import StartHandler, AuthenticationHandler
from .invoices.handlers import InvoiceHandler
from .services.handlers import ServicesHandler
from .tickets.handlers import TicketsHandler
from .FAQ.handlers import FAQHandler
from .logout.handlers import LogOutHandler

from .utils import *
from ..models import User, Authentication


class MessageHandler:
    def __init__(self, bot, data):
        self.bot = bot
        self.data = data

    def get_message_text(self):
        return self.data['message']['text'] if 'text' in self.data['message'].keys() else 'None'

    def get_user_step(self):
        user = User.objects.filter(telegram_id=self.data['message']['from']['id'])
        unauthorized_user = Authentication.objects.filter(telegram_id=self.data['message']['from']['id'])

        if unauthorized_user.exists():
            return unauthorized_user.first().step if unauthorized_user.first().step is not None else ''

        return user.first().step if user.exists() else ''

    def get_user(self):
        user = User.objects.filter(telegram_id=self.data['message']['from']['id'])

        return False if not user.exists() else user.first().telegram_is_authenticate

    def handle_request(self):
        message = self.get_message_text()
        user_step = self.get_user_step()
        is_user_authorize = self.get_user()

        if is_user_authorize:  # access to commands and keyboard
            if message == '/start':
                self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                     text='You are authorized.\n'
                                          'This command will be available after you are logging out.\n\n'
                                          'If you want to log out, just write /logout or click it on keyboard.')
            elif message == '/menu':
                StartHandler.show_menu(self.bot, self.data)
            elif message in ['/invoices', '🧾 Invoices']:
                InvoiceHandler.show_keyboard(self.bot, self.data)
            elif message in ['/services', '👨‍💻 Services']:
                ServicesHandler.show_keyboard(self.bot, self.data)
            elif message in ['/tickets', '📝 Tickets']:
                TicketsHandler.show_keyboard(self.bot, self.data)
            elif message in ['/faq', '⁉️ FAQ']:
                FAQHandler.show_keyboard(self.bot, self.data)
            elif message in ['/logout', '🚪 Log Out']:
                LogOutHandler.show_confirm_keyboard(self.bot, self.data)
            else:
                # steps users ...
                self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                     text='Unknown command, please choose another option',
                                     reply_markup=StartHandler.main_keyboard())
        else:
            authentication: AuthenticationHandler = AuthenticationHandler(self.bot, self.data)

            if message == '/start':
                StartHandler.start(self.bot, self.data)
            elif 'set_email' in user_step:
                authentication.set_user_email(self.data)
            elif 'set_verify_code' in user_step:
                authentication.set_user_verification_code(self.data)
            else:
                self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                     text='Authorization first 🙃\n'
                                          'Use /start and write an email 👇')
