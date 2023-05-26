from authentication.helpers.B24Webhook import set_webhook
from services.models import Service, ServiceCategory
from invoices.models import Invoice, LocalInvoice
from invoices.views import format_price

from telegram import LabeledPrice, PreCheckoutQuery, Message
from bitrix24 import Bitrix24, BitrixError
from .keyboards import *
from ..utils import *

import datetime
import time


class ServicesHandler:
    def __init__(self, bot, data, callback_title):
        self.bot = bot
        self.data = data

        callback_title = callback_title.replace('services_', '')

        if 'pre_checkout_query' in self.data.keys():
            self.set_pre_checkout_query()

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

        elif 'order_' in callback_title:
            service_id = callback_title.split('_')[1]

            self.show_invoice_for_selected_service(service_id)

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
                             reply_markup=selected_category_keyboard(services))

    def show_user_services(self):
        user = get_user(self.data['callback_query'])
        user_invoices = Invoice.objects.filter(responsible=user.b24_contact_id, status__value='Paid')
        user_services_title = [invoice.product_title for invoice in user_invoices]
        if user_invoices:
            user_services = Service.objects.filter(title__in=user_services_title)
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text='You have services!',
                                 reply_markup=user_services_keyboard(user_services))
        else:
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text='You have no services 🙁')

    def show_service_details(self, service_id):
        service = Service.objects.filter(service_id=service_id).order_by('price')
        if service.exists():
            service = service.first()

        more_one = True if Service.objects.filter(category=service.category).count() > 1 else False

        service_title = service.title if service.title else 'Title is empty...'
        service_detail_text = service.detail_text if service.detail_text else 'Detail text is empty...'
        message = format_price(service.price) + ' | ' + service_title + '\n\n' + service_detail_text

        if service.image:
            self.bot.sendPhoto(chat_id=get_chat_id(self.data['callback_query']),
                               photo=service.image,
                               caption=message,
                               reply_markup=service_detail_keyboard(service, more_one))
        else:
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text=message,
                                 reply_markup=service_detail_keyboard(service, more_one))

    def show_invoice_for_selected_service(self, service_id):
        user = get_user(self.data['callback_query'])
        service = Service.objects.filter(service_id=service_id)
        if service.exists():
            service = service.first()

        # Create invoice for selected service
        b24_product_id = service.service_id  # request.POST["b24_product_id"]
        print(b24_product_id)
        product = Service.objects.get(service_id=str(b24_product_id))
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)

        url = set_webhook("crm.product.list")
        bx24 = Bitrix24(url)
        try:
            invoice_id = bx24.callMethod('crm.invoice.add', fields={'ORDER_TOPIC': "Invoice - " + product.title,
                                                                    'PERSON_TYPE_ID': 1,
                                                                    'UF_CONTACT_ID': user.b24_contact_id,  # 1
                                                                    'STATUS_ID': 'N',
                                                                    'RESPONSIBLE_ID': 1,
                                                                    'PAY_SYSTEM_ID': 4,
                                                                    'DATE_PAY_BEFORE': tomorrow.strftime("%m/%d/%Y"),
                                                                    "PRODUCT_ROWS": [
                                                                        {"ID": 0,
                                                                         "PRODUCT_ID": product.service_id,  # product.id
                                                                         "PRODUCT_NAME": product.title,
                                                                         "QUANTITY": 1,
                                                                         "PRICE": product.price},
                                                                    ]})

            time.sleep(3)
            LocalInvoice.objects.create(b24_invoice_id=invoice_id, stripe_price_id=product.stripe_id)
            # invoice = Invoice.objects.get(invoice_id=invoice_id)
        except BitrixError as message:
            print(message)

        # Service detail
        service_title = service.title if service.title else 'Title is empty...'
        service_detail_text = service.detail_text if service.detail_text else 'Detail text is empty...'
        service_price = format_price_for_service(service.price)

        price = LabeledPrice(label=service_title, amount=service_price)

        self.bot.sendInvoice(chat_id=get_chat_id(self.data['callback_query']),
                             title=service_title,
                             description=service_detail_text,
                             payload='services',
                             provider_token='284685063:TEST:NTkwYmE5MGYxNjdh',
                             currency='USD',
                             prices=[price])

    def set_pre_checkout_query(self):

        # Some condition for successful transfer
        self.bot.answerPreCheckoutQuery(pre_checkout_query_id=self.data['pre_checkout_query']['id'], ok=True)
