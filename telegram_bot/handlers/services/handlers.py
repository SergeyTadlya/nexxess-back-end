from services.models import Service
from invoices.views import format_price

from .keyboards import *
from ..utils import *


class ServicesHandler:
    def __init__(self, bot, data, callback_title):
        self.bot = bot
        self.data = data

        callback_title = callback_title.replace('services_', '')

        if callback_title == 'menu':
            self.show_services_menu(self.bot, self.data['callback_query'])

        elif callback_title == 'my':
            self.show_user_services()

        elif callback_title == 'all':
            self.show_all_services_type()

        elif callback_title == 'consultations':
            pass

        elif callback_title == 'books':
            pass

        elif callback_title == 'packages':
            pass

        elif callback_title[:2] == 'id':
            service_id = callback_title[3:]

            self.show_service_details(service_id)

    @staticmethod
    def show_services_menu(bot, data):
        bot.sendMessage(chat_id=get_chat_id(data),
                        text='Choose the option',
                        reply_markup=services_menu_keyboard())

    def show_all_services_type(self):
        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text='Choose the type of services',
                             reply_markup=all_services_keyboard())

    def show_user_services(self):
        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text='You have no services')

    def show_service_details(self, service_id):
        service = Service.objects.filter(service_id=service_id)
        if service.exists():
            service = service.first()

        self.bot.sendPhoto(chat_id=get_chat_id(self.data['callback_query']),
                           photo=service.image,
                           caption=f'{format_price(service.price)} | {service.title}\n\n'
                                   f'{service.title_description}',
                           reply_markup=service_detail_keyboard(service))
