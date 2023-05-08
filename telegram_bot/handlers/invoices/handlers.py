from .keyboards import *
from .utils import *
from ..utils import *


class InvoiceHandler:
    def __init__(self, bot, data, callback_title):
        self.bot = bot
        self.data = data

        callback_title = callback_title.replace('invoices_', '')

        if callback_title == 'statuses':
            self.show_invoices_menu(self.bot, self.data['callback_query'])

        elif 'invoiceId' in callback_title:
            parsed_data = callback_title.split('_')

            status = parsed_data[0] if parsed_data[0] == 'All' else None
            current_page = parsed_data[1]
            invoice_id = parsed_data[3]

            self.show_invoice_details(invoice_id, current_page, status)

        elif 'New' in callback_title:
            status = callback_title.split('_')[0]
            current_page = get_current_page(callback_title)

            self.show_new_invoices(status, current_page)

        elif 'Paid' in callback_title:
            status = callback_title.split('_')[0]
            current_page = get_current_page(callback_title)

            self.show_paid_invoices(status, current_page)

        elif 'Unpaid' in callback_title:
            status = callback_title.split('_')[0]
            current_page = get_current_page(callback_title)

            self.show_unpaid_invoices(status, current_page)

        elif 'All' in callback_title:
            current_page = get_current_page(callback_title)
            self.show_all_invoices(current_page)

    @staticmethod
    def show_invoices_menu(bot, data):
        user = get_user(data)
        invoices = get_invoices(user.email)

        invoices_quantity_by_status = {
            'new': str(len(invoices.filter(status__value='New'))),
            'paid': str(len(invoices.filter(status__value='Paid'))),
            'unpaid': str(len(invoices.filter(status__value='Unpaid'))),
            'all': str(len(invoices))
        }

        bot.sendMessage(chat_id=get_chat_id(data),
                        text='Choose the status',
                        reply_markup=invoices_statuses_keyboard(invoices_quantity_by_status))

    def show_new_invoices(self, status, current_page=1):
        user = get_user(self.data['callback_query'])
        new_invoices = get_invoices(user.email, status)
        invoices_pagination = do_pagination(new_invoices, current_page, 2)

        if invoices_pagination['quantity'] > 0:
            invoices = invoices_pagination['invoices']
            all_pages = invoices_pagination['all_pages']
            has_pages = invoices_pagination['has_pages']

            try:
                self.bot.edit_message_text(
                    f"New invoices: ",
                    chat_id=get_chat_id(self.data['callback_query']),
                    message_id=self.data['callback_query']['message']['message_id'],
                    reply_markup=new_invoices_keyboard(invoices, current_page, all_pages, has_pages)
                )
            except Exception as e:
                print(e)
        else:
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text='You don`t have any invoices')

    def show_paid_invoices(self, status, current_page=1):
        user = get_user(self.data['callback_query'])
        paid_invoices = get_invoices(user.email, status)
        invoices_pagination = do_pagination(paid_invoices, current_page, 2)

        if invoices_pagination['quantity'] > 0:
            invoices = invoices_pagination['invoices']
            all_pages = invoices_pagination['all_pages']
            has_pages = invoices_pagination['has_pages']

            try:
                self.bot.edit_message_text(
                    f"Paid invoices: ",
                    chat_id=get_chat_id(self.data['callback_query']),
                    message_id=self.data['callback_query']['message']['message_id'],
                    reply_markup=paid_invoices_keyboard(invoices, current_page, all_pages, has_pages)
                )
            except Exception as e:
                print(e)
        else:
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text='You don`t have any invoices')

    def show_unpaid_invoices(self, status, current_page=1):
        user = get_user(self.data['callback_query'])
        unpaid_invoices = get_invoices(user.email, status)
        invoices_pagination = do_pagination(unpaid_invoices, current_page, 2)

        if invoices_pagination['quantity'] > 0:
            invoices = invoices_pagination['invoices']
            all_pages = invoices_pagination['all_pages']
            has_pages = invoices_pagination['has_pages']

            try:
                self.bot.edit_message_text(
                    f"Unpaid invoices: ",
                    chat_id=get_chat_id(self.data['callback_query']),
                    message_id=self.data['callback_query']['message']['message_id'],
                    reply_markup=unpaid_invoices_keyboard(invoices, current_page, all_pages, has_pages)
                )
            except Exception as e:
                print(e)
        else:
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text='You don`t have any invoices')

    def show_all_invoices(self, current_page=1):
        user = get_user(self.data['callback_query'])
        all_invoices = get_invoices(user.email)
        invoices_pagination = do_pagination(all_invoices, current_page, 2)

        if invoices_pagination['quantity'] > 0:
            invoices = invoices_pagination['invoices']
            all_pages = invoices_pagination['all_pages']
            has_pages = invoices_pagination['has_pages']

            try:
                self.bot.edit_message_text(
                    f"All invoices: ",
                    chat_id=get_chat_id(self.data['callback_query']),
                    message_id=self.data['callback_query']['message']['message_id'],
                    reply_markup=all_invoices_keyboard(invoices, current_page, all_pages, has_pages)
                )
            except Exception as e:
                print(e)
        else:
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text='You don`t have any invoices')

    def show_invoice_details(self, invoice_id, current_page, status_all):
        invoice = get_invoice_by_id(invoice_id)
        user = get_user(self.data['callback_query'])
        status = invoice.status.value if status_all is None else status_all

        # file_path = set_file_path(invoice)  Set file path by status
        file_path = generate_new_pdf(user, invoice, 'invoices/PDF_templates/invoice_ordinary.pdf')
        filename = invoice.invoice_id + '_' + invoice.status.value

        invoice_detail = 'Invoice ID: ' + invoice.invoice_id + '\n' + \
                         'Price: ' + format_price(invoice.price) + '\n' + \
                         'Status: ' + invoice.status.value + '\n' + \
                         'Date: ' + format_date(invoice.date) + '\n' + \
                         'Due date: ' + format_date(invoice.due_date) + '\n'

        self.bot.send_document(chat_id=get_chat_id(self.data['callback_query']),
                               document=open(file_path, 'rb'),
                               filename=filename)

        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text=invoice_detail,
                             reply_markup=invoice_details_keyboard(status, current_page))
