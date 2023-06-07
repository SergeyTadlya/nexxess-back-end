from .invoices.handlers import InvoiceHandler
from .services.handlers import ServicesHandler
from .tickets.handlers import TicketsHandler
from .logout.handlers import LogOutHandler

from .utils import MyStyleCalendar, LSTEP, get_chat_id
from ..models import User

from datetime import date

import logging


logger = logging.getLogger(__name__)


class CallbackHandler:
    def __init__(self, bot, data):
        self.bot = bot
        self.data = data

    def get_callback_data(self):
        return self.data['callback_query']['data'] if 'callback_query' in self.data.keys() else ''

    def get_invoice_payload(self):
        return self.data['pre_checkout_query']['invoice_payload'] if 'pre_checkout_query' in self.data.keys() else ''

    def get_user(self):
        if 'pre_checkout_query' in self.data.keys():
            username = self.data['pre_checkout_query']['from']['username']
        elif 'successful_payment' in self.data.keys():
            username = self.data['successful_payment']['from']['username']
        else:
            username = self.data['callback_query']['from']['username']

        return User.objects.filter(telegram_username=username).first()

    def handle_request(self):
        callback_data = self.get_callback_data()
        invoice_payload = self.get_invoice_payload()

        user = self.get_user()
        if user.telegram_is_authenticate:

            if 'invoices' in callback_data:
                InvoiceHandler(self.bot, self.data, callback_data)

            elif 'services' in callback_data + invoice_payload:
                ServicesHandler(self.bot, self.data, callback_data)

            elif 'tickets' in callback_data:
                TicketsHandler(self.bot, self.data, callback_data)

            elif 'faq' in callback_data:
                pass

            elif 'logout' in callback_data:
                LogOutHandler(self.bot, self.data, callback_data)

            elif 'cbcal' in callback_data:
                result, key, step = MyStyleCalendar(min_date=date.today()).process(self.data['callback_query']['data'])
                if not result and key:
                    try:
                        self.bot.edit_message_text(f"Select {LSTEP[step]} for deadline:",
                                                   self.data['callback_query']['message']['chat']['id'],
                                                   self.data['callback_query']['message']['message_id'],
                                                   reply_markup=key)
                    except Exception as e:
                        # Exception logger credentials
                        user_chat_id = self.data['callback_query']['message']['chat']['id']
                        username = self.data['callback_query']['message']['chat']['username']

                        logger.error('Exception: ' + user_chat_id + ' (' + username + ') - ' + str(e))

                elif isinstance(result, date):
                    try:
                        due_date = result.strftime('%Y-%m-%d')
                        self.bot.edit_message_text('Deadline is ' + due_date + '\n\n' + \
                                                   'Wait a few seconds while the ticket is being created',
                                                   self.data['callback_query']['message']['chat']['id'],
                                                   self.data['callback_query']['message']['message_id'])
                        TicketsHandler.create_new_ticket(self.bot, self.data, due_date)
                    except Exception as e:
                        # Exception logger credentials
                        user_chat_id = self.data['callback_query']['message']['chat']['id']
                        username = self.data['callback_query']['message']['chat']['username']

                        logger.error('Exception: ' + user_chat_id + ' (' + username + ') - ' + str(e))
        else:
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text='Authorization first 🙃\n'
                                      'Use /start and then write your email 👇')
