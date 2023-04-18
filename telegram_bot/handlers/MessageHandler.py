from .utils import *
from ..models import User, Authentication
from .start.handlers import StartHandler, AuthenticationHandler
from .invoices.handlers import InvoiceHandler
from .services.handlers import ServicesHandler
from .tickets.handlers import TicketsHandler
from .FAQ.handlers import FAQHandler
from .logout.handlers import LogOutHandler


class MessageHandler:
    def __init__(self, bot, data):
        self.bot = bot
        self.data = data

    def get_message_text(self):
        return self.data['message']['text'] if 'sticker' not in self.data['message'].keys() else ''

    def get_user_step(self):
        user = User.objects.filter(telegram_id=self.data['message']['from']['id'])
        unauthorized_user = Authentication.objects.filter(telegram_id=self.data['message']['from']['id'])

        if unauthorized_user.exists():
            return unauthorized_user.first().step if unauthorized_user.first().step is not None else ''

        return user.first().step if user.exists() else ''

    def get_user(self):
        user = User.objects.filter(telegram_id=self.data['message']['from']['id'])

        return False if not user.exists() else user.first().is_active

    def handle_request(self):
        message = self.get_message_text()
        user_step = self.get_user_step()
        is_user_active = self.get_user()

        if is_user_active:
            if message == '/menu':
                pass
            elif message == '/invoices' or message == '🧾 Invoices':
                InvoiceHandler.show_keyboard(self.bot, self.data)
            elif message == '/services' or message == '👨‍💻 Services':
                ServicesHandler.show_keyboard(self.bot, self.data)
            elif message == '/tickets' or message == '📝 Tickets':
                TicketsHandler.show_keyboard(self.bot, self.data)
            elif message == '/faq' or message == '⁉️ FAQ':
                FAQHandler.show_keyboard(self.bot, self.data)
            elif message == '/logout' or message == '🚪 Log Out':
                LogOutHandler.show_confirm_keyboard(self.bot, self.data)
            else:
                # steps users ...
                self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                     text='Unknown command, please choose another option',
                                     reply_markup=StartHandler.main_keyboard())
        else:
            authentication_main: AuthenticationHandler = AuthenticationHandler(self.bot, self.data)

            if message == '/start':
                StartHandler.start(self.bot, self.data)
            elif 'set_email' in user_step:
                authentication_main.set_user_email(self.data)
            elif 'set_password' in user_step:
                authentication_main.set_user_password(self.data)
            else:
                self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                     text='Authorization first')
