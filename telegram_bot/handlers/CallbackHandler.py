from ..models import User
from .invoices.handlers import InvoiceHandler
from .logout.handlers import LogOutHandler


class CallbackHandler:
    def __init__(self, bot, data):
        self.bot = bot
        self.data = data

    def get_callback_text(self):
        return self.data['callback_query']['data']

    def get_user_step(self):
        user = User.objects.filter(telegram_id=self.data['callback_query']['from']['id'])

        return user.first().step if user.exists() else ''

    def handle_request(self):
        callback_data = self.get_callback_text()
        print(callback_data)

        if 'invoices' in callback_data:
            InvoiceHandler(self.bot, self.data, callback_data)
        elif 'services' in callback_data:
            pass
        elif 'tickets' in callback_data:
            pass
        elif 'FAQ' in callback_data:
            pass
        elif 'logout' in callback_data:
            LogOutHandler(self.bot, self.data, callback_data)


