from services.models import Service, ServiceCategory
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

        elif 'ctg_' in callback_title:
            category_name = callback_title.split('_')[1]

            self.show_selected_category(category_name)

        elif 'detail_' in callback_title:
            service_id = callback_title.split('_')[1]

            self.show_service_details(service_id)

    @staticmethod
    def show_services_menu(bot, data):
        bot.sendMessage(chat_id=get_chat_id(data),
                        text='Choose the option:',
                        reply_markup=services_menu_keyboard())

    def show_all_services_type(self):
        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text='Choose the type of services:',
                             reply_markup=all_services_keyboard())

    def show_selected_category(self, category_name):
        services = Service.objects.filter(category__category_name__startswith=category_name)

        if category_name == 'C':
            message = '👥 Hourly rate chart for consultation: '
        elif category_name == 'B':
            message = '📚 Nexxess trust books: '
        else:
            message = '📦 Nexxess packages: '

        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text=message,
                             reply_markup=selected_category_keyboard(services, category_name))

    def show_user_services(self):
        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text='You have no services 🙁')

    def show_service_details(self, service_id):
        service = Service.objects.filter(service_id=service_id).order_by('price')
        if service.exists():
            service = service.first()

        service_title = service.title if service.title else 'Title is empty...'
        service_detail_text = service.detail_text if service.detail_text else 'Detail text is empty...'
        message = format_price(service.price) + ' | ' + service_title + '\n\n' + service_detail_text

        if service.image:
            self.bot.sendPhoto(chat_id=get_chat_id(self.data['callback_query']),
                               photo=service.image,
                               caption=message,
                               reply_markup=service_detail_keyboard(service))
        else:
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text=message,
                                 reply_markup=service_detail_keyboard(service))
