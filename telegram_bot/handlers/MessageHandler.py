from ..models import User, Authentication
from .start.handlers import StartHandler, AuthenticationHandler
from .invoices.handlers import InvoiceHandler
from .services.handlers import ServicesHandler
from .tickets.handlers import TicketsHandler
from .FAQ.handlers import FAQHandler


class MessageHandler:
    def __init__(self, bot, data):
        self.bot = bot
        self.data = data

    def get_message_text(self):
        return self.data['message']['text']

    def get_user_step(self):
        user = User.objects.filter(telegram_id=self.data['message']['from']['id'])
        unauthorized_user = Authentication.objects.filter(telegram_id=self.data['message']['from']['id'])

        if unauthorized_user.exists():
            return unauthorized_user.first().step if unauthorized_user.first().step is not None else ''

        return user.first().step if user.exists() else ''

    def handle_request(self):
        message = self.get_message_text()

        if message == '/start':
            StartHandler.start(self.bot, self.data)
        elif message == '/invoices' or message == '🧾 Invoices':
            InvoiceHandler.show_keyboard(self.bot, self.data)
        elif message == '/services' or message == '👨‍💻 Services':
            ServicesHandler.show_keyboard(self.bot, self.data)
        elif message == '/tickets' or message == '📝 Tickets':
            TicketsHandler.show_keyboard(self.bot, self.data)
        elif message == '/faq' or message == '⁉️ FAQ':
            FAQHandler.show_keyboard(self.bot, self.data)
        elif message == '/logout' or message == '🚪 Log Out':
            pass
        else:
            user_step = self.get_user_step()

            authentication_main: AuthenticationHandler = AuthenticationHandler(self.bot, self.data)

            if 'set_email' in user_step:
                authentication_main.set_user_email(self.data)
            elif 'set_password' in user_step:
                authentication_main.set_user_password(self.data)
            else:
                self.bot.sendMessage(chat_id=self.data['message']['chat']['id'],
                                     text='Unknown command, please choose another option',
                                     reply_markup=StartHandler.main_keyboard())
