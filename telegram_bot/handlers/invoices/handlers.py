from .keyboards import *
from .utils import *
from ..utils import *

from invoices.models import Invoice, Status
from services.models import Service

import logging


logger = logging.getLogger(__name__)


class InvoiceHandler:
    def __init__(self, bot, data, callback_title):
        self.bot = bot
        self.data = data

        callback_title = callback_title.replace('invoices_', '')

        if callback_title == 'statuses':
            self.show_invoices_menu(self.bot, self.data['callback_query'])

        elif 'detail' in callback_title:
            parsed_data = callback_title.split('_')
            status_name, current_page, invoice_id = parsed_data[1], parsed_data[2], parsed_data[4]

            self.show_invoice_details(status_name, current_page, invoice_id)

        elif 'status_All' in callback_title:
            parsed_data = callback_title.split('_')
            current_page = int(parsed_data[2])

            self.show_all_invoices(current_page)

        elif 'status_' in callback_title:
            parsed_data = callback_title.split('_')
            status_name, current_page = parsed_data[1], int(parsed_data[2])

            self.show_invoices_for_selected_status(status_name, current_page)

    @staticmethod
    def show_invoices_menu(bot, data):
        user = get_user(data)
        invoices_statuses = Status.objects.all()
        invoices = Invoice.objects.filter(responsible=str(user.b24_contact_id))

        bot.sendMessage(chat_id=get_chat_id(data),
                        text='Choose the status',
                        reply_markup=invoices_statuses_keyboard(invoices, invoices_statuses))

    def show_invoices_for_selected_status(self, status_name, current_page, element_on_page=8):
        user = get_user(self.data['callback_query'])
        invoice_status = Status.objects.get(value=status_name)
        invoices = Invoice.objects.filter(responsible=str(user.b24_contact_id), status=invoice_status).order_by('-date')

        invoices_quantity = len(invoices)
        if invoices_quantity == 0:
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text='You don`t have any ' + status_name.lower() + ' invoices')
            return

        all_pages = invoices_quantity // element_on_page if not invoices_quantity % element_on_page else (invoices_quantity // element_on_page) + 1
        has_pages = False

        if invoices_quantity > element_on_page:
            has_pages = True
            invoices = invoices[element_on_page * (current_page - 1):element_on_page * current_page]

        try:
            message = invoice_status.sticker + ' ' + invoice_status.value + ' invoices: '
            self.bot.edit_message_text(
                message,
                chat_id=get_chat_id(self.data['callback_query']),
                message_id=self.data['callback_query']['message']['message_id'],
                reply_markup=invoices_for_selected_status_keyboard(invoices, invoice_status, current_page, all_pages, has_pages)
            )
        except Exception as e:
            # Exception logger credentials
            user_chat_id = str(user.telegram_id)
            username = user.telegram_username

            logger.error('Exception: ' + user_chat_id + ' (' + username + ') - ' + str(e))

    def show_all_invoices(self, current_page, element_on_page=8):
        user = get_user(self.data['callback_query'])
        invoices = Invoice.objects.filter(responsible=str(user.b24_contact_id)).order_by('-date')

        invoices_quantity = len(invoices)
        if invoices_quantity == 0:
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text='You don`t have any invoices')
            return

        all_pages = invoices_quantity // element_on_page if not invoices_quantity % element_on_page else (invoices_quantity // element_on_page) + 1
        has_pages = False

        if invoices_quantity > element_on_page:
            has_pages = True
            invoices = invoices[element_on_page * (current_page - 1):element_on_page * current_page]

        try:
            self.bot.edit_message_text(
                'All invoices: ',
                chat_id=get_chat_id(self.data['callback_query']),
                message_id=self.data['callback_query']['message']['message_id'],
                reply_markup=all_invoices_keyboard(invoices, current_page, all_pages, has_pages)
            )
        except Exception as e:
            # Exception logger credentials
            user_chat_id = str(user.telegram_id)
            username = user.telegram_username

            logger.error('Exception: ' + user_chat_id + ' (' + username + ') - ' + str(e))

    def show_invoice_details(self, status_name, current_page, invoice_id):
        invoice = get_invoice_by_id(invoice_id, status_name)
        user = get_user(self.data['callback_query'])

        # file_path = set_file_path(invoice)  Set file path by status
        if status_name == 'Paid':
            file_path = generate_new_pdf(user, invoice, 'invoices/PDF_templates/invoice_template.pdf')
        else:
            file_path = generate_new_pdf(user, invoice, 'invoices/PDF_templates/invoice_ordinary.pdf')

        service = Service.objects.get(service_id=invoice.service_id)
        service_description = service.detail_text if service.detail_text else 'Detail text is empty'
        invoice_detail = '-------------------- Invoice --------------------' + '\n' + \
                         'Invoice ID: ' + invoice.invoice_id + '\n' + \
                         'Price: ' + format_price(invoice.price) + '\n' + \
                         'Status: ' + invoice.status.value + '\n' + \
                         'Date: ' + format_date(invoice.date) + '\n' + \
                         'Due date: ' + format_date(invoice.due_date) + '\n\n' + \
                         '-------------------- Service --------------------' + '\n' + \
                         'Title: ' + service.title + '\n' + \
                         'Category: ' + service.category.category_name + '\n' + \
                         'Description: ' + service_description

        filename = invoice.invoice_id + '_' + invoice.status.value
        self.bot.send_document(chat_id=get_chat_id(self.data['callback_query']),
                               document=open(file_path, 'rb'),
                               filename=filename + '.pdf')

        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text=invoice_detail,
                             reply_markup=invoice_details_keyboard(status_name, current_page, invoice))
