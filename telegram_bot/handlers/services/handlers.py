from authentication.helpers.B24Webhook import set_webhook
from services.models import Service, ServiceCategory
from invoices.models import Invoice, LocalInvoice, StripeSettings, Status
from invoices.views import format_price, format_date

from telegram import LabeledPrice, PreCheckoutQuery, Message
from bitrix24 import Bitrix24, BitrixError
from .keyboards import *
from ..utils import *

import datetime


class ServicesHandler:
    def __init__(self, bot, data, callback_title):
        self.bot = bot
        self.data = data

        if 'pre_checkout_query' in self.data.keys():
            service_id = self.data['pre_checkout_query']['invoice_payload'].split('_')[1]
            self.set_pre_checkout_query(service_id)

        callback_title = callback_title.replace('services_', '')

        if callback_title == 'menu':
            self.show_services_menu(self.bot, self.data['callback_query'])

        elif callback_title == 'my':
            self.show_user_services()

        elif 'detailMy_' in callback_title:
            invoice_id = callback_title.split('_')[1]
            self.show_detail_user_service(invoice_id)

        elif callback_title == 'all':
            self.show_all_services_type()

        elif 'ctg_' in callback_title:
            category_name = callback_title.split('_')[1]
            self.show_selected_category(category_name)

        elif 'info_' in callback_title:
            parsed_data = callback_title.split('_')
            service_id = parsed_data[1]
            delete_message = parsed_data[2] if 'del' in parsed_data else False

            self.show_service_info(service_id, delete_message)

        elif 'order_' in callback_title:
            service_id = callback_title.split('_')[1]

            self.show_invoice_for_selected_service(service_id)

        elif 'detail_' in callback_title:
            invoice_id = callback_title.split('_')[1]
            self.show_service_detail(invoice_id)

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

        if category_name == 'B':
            message = '📚 Nexxess trust books: '
        elif category_name == 'P':
            message = '📦 Nexxess packages: '
        else:
            message = 'Unknown category'

        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text=message,
                             reply_markup=selected_category_keyboard(services))

    def show_user_services(self):
        user = get_user(self.data['callback_query'])
        user_invoices = Invoice.objects.filter(responsible=user.b24_contact_id, status__value='Paid')
        user_services_id = [invoice.service_id for invoice in user_invoices]

        if user_invoices:
            user_services = Service.objects.filter(service_id__in=user_services_id).order_by('category')
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text='You have services!',
                                 reply_markup=user_services_keyboard(user_services))
        else:
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text='You have no services 🙁')

    def show_detail_user_service(self, service_id):
        service = Service.objects.filter(service_id=service_id)
        if service.exists():
            service = service.first()

        service_info_text = service.detail_text if service.detail_text else 'Detail text is empty...'
        service_description = '----------------------  Service  ----------------------' + '\n' + \
                              'Title: ' + service.title + '\n' + \
                              'Category: ' + service.category.category_name + '\n' + \
                              'Description: ' + service_info_text + '\n\n'
        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text=service_description,
                             reply_markup=back_to_my_services_keyboard())

    # Just show service info before payment
    def show_service_info(self, service_id, delete_message):
        service = Service.objects.filter(service_id=service_id).order_by('price')
        if service.exists():
            service = service.first()

        more_one = True if Service.objects.filter(category=service.category).count() > 1 else False

        service_info_text = service.detail_text if service.detail_text else 'Detail text is empty...'
        message = format_price(service.price) + ' | ' + service.title + '\n\n' + service_info_text

        if delete_message:
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text=message,
                                 reply_markup=service_info_keyboard(service, more_one))
            self.bot.deleteMessage(message_id=self.data['callback_query']['message']['message_id'],
                                   chat_id=get_chat_id(self.data['callback_query']))
        else:
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text=message,
                                 reply_markup=service_info_keyboard(service, more_one))

    # Show service data for payment or just info if service already paid
    def show_service_detail(self, invoice_id):
        invoice = Invoice.objects.filter(invoice_id=invoice_id)
        if invoice.exists():
            invoice = invoice.first()

        service = Service.objects.filter(service_id=invoice.service_id)
        if service.exists():
            service = service.first()

        service_info_text = service.detail_text if service.detail_text else 'Detail text is empty...'
        if invoice.status.value == 'Paid':
            invoice_detail = '----------------------  Service  ----------------------' + '\n' + \
                             'Title: ' + service.title + '\n' + \
                             'Category: ' + service.category.category_name + '\n' + \
                             'Description: ' + service_info_text + '\n\n' + \
                             '----------------------  Invoice  ----------------------' + '\n' + \
                             'Id: ' + invoice.invoice_id + '\n' + \
                             'Price: ' + format_price(invoice.price) + '\n' + \
                             'Status: ' + invoice.status.sticker + ' ' + invoice.status.value + '\n' + \
                             'Date: ' + format_date(invoice.date) + '\n' + \
                             'Due date: ' + format_date(invoice.due_date)
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text=invoice_detail,
                                 reply_markup=invoice_for_selected_service_keyboard(service, invoice))

        else:
            # Message about invoice
            invoice_detail = '----------------------  Invoice  ----------------------' + '\n' + \
                             'Id: ' + invoice.invoice_id + '\n' + \
                             'Price: ' + format_price(invoice.price) + '\n' + \
                             'Status: ' + invoice.status.sticker + ' ' + invoice.status.value + '\n' + \
                             'Date: ' + format_date(invoice.date) + '\n' + \
                             'Due date: ' + format_date(invoice.due_date)
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text=invoice_detail)

            # Message about service payment
            price = [LabeledPrice(label=service.title, amount=format_price_for_service(service.price))]
            stripe = StripeSettings.objects.get(id=1)
            self.bot.sendInvoice(chat_id=get_chat_id(self.data['callback_query']),
                                 title=service.title,
                                 description=service_info_text,
                                 payload='services_' + str(invoice_id),
                                 provider_token=stripe.telegram_provider_token,
                                 currency='USD',
                                 prices=price,
                                 reply_markup=invoice_for_selected_service_keyboard(service, invoice))

    def show_invoice_for_selected_service(self, service_id):
        user = get_user(self.data['callback_query'])
        user_invoices = Invoice.objects.filter(responsible=str(user.b24_contact_id))
        user_services_id = [invoice.service_id for invoice in user_invoices]

        # Checking if the user has already ordered or bought the current service
        service = Service.objects.filter(service_id=service_id)
        if service.exists():
            service = service.first()

            if service.service_id in user_services_id:
                user_invoice = user_invoices.filter(service_id=service.service_id).first()

                if user_invoice.status.value == 'Paid':
                    self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                         text='You have already purchased this service 😅',
                                         reply_markup=already_existing_service_keyboard(user_invoice))
                else:
                    self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                         text='You have already ordered this service 🙂',
                                         reply_markup=already_existing_service_keyboard(user_invoice))
                return

        # Create invoice in bitrix for selected service
        try:
            b24_product_id = service.service_id
            product = Service.objects.get(service_id=str(b24_product_id))
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)

            url = set_webhook("crm.product.list")
            bx24 = Bitrix24(url)

            invoice_id = bx24.callMethod('crm.invoice.add', fields={'ORDER_TOPIC': "Invoice - " + product.title,
                                                                    'PERSON_TYPE_ID': 1,
                                                                    'UF_CONTACT_ID': user.b24_contact_id,
                                                                    'STATUS_ID': 'N',
                                                                    'RESPONSIBLE_ID': 1,
                                                                    'PAY_SYSTEM_ID': 4,
                                                                    'DATE_PAY_BEFORE': tomorrow.strftime("%m/%d/%Y"),
                                                                    "PRODUCT_ROWS": [
                                                                        {"ID": 0,
                                                                         "PRODUCT_ID": product.service_id,
                                                                         "PRODUCT_NAME": product.title,
                                                                         "QUANTITY": 1,
                                                                         "PRICE": product.price},
                                                                    ]})
            LocalInvoice.objects.create(b24_invoice_id=invoice_id, stripe_price_id=product.stripe_id)
        except BitrixError as error_message:
            print(error_message)

        # Service data
        service_title = service.title if service.title else 'Title is empty...'
        service_info_text = service.detail_text if service.detail_text else 'Detail text is empty...'
        service_price = format_price_for_service(service.price)
        price = [LabeledPrice(label=service_title, amount=service_price)]

        # Send invoice to user
        stripe = StripeSettings.objects.get(id=1)
        self.bot.sendInvoice(chat_id=get_chat_id(self.data['callback_query']),
                             title=service_title,
                             description=service_info_text,
                             payload='services_' + str(invoice_id),
                             provider_token=stripe.telegram_provider_token,
                             currency='USD',
                             prices=price,
                             reply_markup=invoice_for_selected_service_keyboard(service))

    def set_pre_checkout_query(self, invoice_id):
        user = User.objects.filter(telegram_id=self.data['pre_checkout_query']['from']['id']).first()
        invoice = Invoice.objects.filter(responsible=str(user.b24_contact_id), invoice_id=invoice_id).first()

        if not invoice.status.value == 'Paid':
            self.bot.answerPreCheckoutQuery(pre_checkout_query_id=self.data['pre_checkout_query']['id'],
                                            ok=True,
                                            timeout=5)
            invoice.status = Status.objects.get(value='Paid')
            invoice.save()
        else:
            self.bot.answerPreCheckoutQuery(pre_checkout_query_id=self.data['pre_checkout_query']['id'],
                                            ok=False,
                                            error_message='This invoice has already been paid',
                                            timeout=5)
