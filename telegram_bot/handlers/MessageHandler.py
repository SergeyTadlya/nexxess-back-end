from .start.handlers import StartHandler, AuthenticationHandler
from .invoices.handlers import InvoiceHandler
from .services.handlers import ServicesHandler
from .tickets.handlers import TicketsHandler
from .FAQ.handlers import FAQHandler
from .logout.handlers import LogOutHandler

from .utils import *
from .system_commands import set_up_commands
from ..models import User, Authentication


class MessageHandler:
    def __init__(self, bot, data):
        self.bot = bot
        self.data = data

    def get_message_text(self):
        data_message_keys = self.data['message'].keys()

        if 'text' in data_message_keys:
            return self.data['message']['text']

        elif 'pre_checkout_query' in self.data.keys():
            return 'Without message'

        elif 'successful_payment' in data_message_keys:
            self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                 text='The payment was made successfully')
            return 'Without message'
        else:
            'None'

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
            if message == '/start' and not user_step:
                self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                     text='You are authorized.\n'
                                          'This command will be available after you are logging out.\n\n'
                                          'If you want to log out, just write /logout or click it on keyboard.')
            elif message == '/menu' and not user_step:
                set_up_commands(self.bot)
                StartHandler.show_menu(self.bot, self.data)

            elif message in ['/invoices', '🧾 Invoices'] and not user_step:
                InvoiceHandler.show_invoices_menu(self.bot, self.data)

            elif message in ['/services', '👨‍💻 Services'] and not user_step:
                ServicesHandler.show_services_menu(self.bot, self.data)

            elif message in ['/tickets', '📝 Tickets'] and not user_step:
                TicketsHandler.show_tickets_menu(self.bot, self.data)

            elif message in ['/faq', '⁉️ FAQ'] and not user_step:
                FAQHandler.show_faq_menu(self.bot, self.data)

            elif message in ['/logout', '🚪 Log Out'] and not user_step:
                LogOutHandler.show_confirm_keyboard(self.bot, self.data)

            elif message == 'Without message':
                pass

            else:
                if user_step:  # user_step is not None and not user_step == ''
                    # steps users ...
                    tickets: TicketsHandler = TicketsHandler(self.bot, self.data, '')
                    if 'SET_TICKET_TITLE' in user_step:
                        tickets.save_ticket_title(message)
                    elif 'SET_TICKET_DESCRIPTION' in user_step:
                        tickets.save_ticket_description(message)
                else:
                    self.bot.sendMessage(
                        chat_id=get_chat_id(self.data),
                        text='Nothing is clear, try again',  # Unknown command, please choose another option
                        reply_markup=StartHandler.main_keyboard()
                    )
        else:
            authentication: AuthenticationHandler = AuthenticationHandler(self.bot, self.data)

            if message == '/start':
                StartHandler.start(self.bot, self.data)
            elif 'SET_EMAIL' in user_step:
                authentication.set_user_email(self.data)
            elif 'SET_VERIFY_CODE' in user_step:
                authentication.set_user_verification_code(self.data)
            else:
                self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                     text='Authorization first 🙃\n'
                                          'Use /start and then write your email 👇')
