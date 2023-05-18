from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from invoices.views import format_date, format_price


def invoices_statuses_keyboard(invoices, invoices_statuses) -> InlineKeyboardMarkup:
    buttons = []

    for invoice_status in invoices_statuses:
        text = invoice_status.sticker + ' ' + invoice_status.value + ' (' + str(invoices.filter(status__value=invoice_status.value).count()) + ')'
        callback_data = 'invoices_status_' + invoice_status.value + '_1'

        buttons.append([InlineKeyboardButton(text, callback_data=callback_data)])

    buttons.append([InlineKeyboardButton('All invoices (' + str(len(invoices)) + ')', callback_data='invoices_status_All_1')])

    return InlineKeyboardMarkup(buttons)


def invoices_for_selected_status_keyboard(invoices, status, current_page, all_pages, has_pages):
    buttons = list()

    for invoice in invoices:
        invoice_detail = '#' + invoice.invoice_id + ' | ' + format_price(invoice.price) + ' | ' + format_date(invoice.date)
        invoice_callback_data = 'invoices_status_' + status.value + '_' + str(current_page) + '_detail_' + invoice.invoice_id

        buttons.append([InlineKeyboardButton(invoice_detail, callback_data=invoice_callback_data)])

    if has_pages:
        callback_data_right = 'invoices_status_' + status.value + '_' + str(current_page - 1) if not current_page == 1 else 'Stop'
        callback_data_left = 'invoices_status_' + status.value + '_' + str(current_page + 1) if not current_page == all_pages else 'Stop'
        right = '➡️' if not current_page == all_pages else '🚫'
        left = '⬅️' if not current_page == 1 else '🚫'

        buttons.append([
            InlineKeyboardButton(left, callback_data=callback_data_right),
            InlineKeyboardButton(str(current_page) + '/' + str(all_pages), callback_data='Stop'),
            InlineKeyboardButton(right, callback_data=callback_data_left)
        ])

    buttons.append([InlineKeyboardButton('⬅️ Back to invoices statuses', callback_data='invoices_statuses')])

    return InlineKeyboardMarkup(buttons)


def all_invoices_keyboard(invoices, current_page, all_pages, has_pages) -> InlineKeyboardMarkup:
    buttons = list()

    for invoice in invoices:
        invoice_detail = invoice.status.sticker + ' #' + invoice.invoice_id + ' | ' + format_price(invoice.price) + ' | ' + format_date(invoice.date)
        invoice_callback_data = 'invoices_status_All_' + str(current_page) + '_detail_' + invoice.invoice_id

        buttons.append([InlineKeyboardButton(invoice_detail, callback_data=invoice_callback_data)])

    if has_pages:
        callback_data_left = 'invoices_status_All_' + str(current_page - 1) if not current_page == 1 else 'Stop'
        callback_data_right = 'invoices_status_All_' + str(current_page + 1) if not current_page == all_pages else 'Stop'
        left = '⬅️' if not current_page == 1 else '🚫'
        right = '➡️' if not current_page == all_pages else '🚫'

        buttons.append([
            InlineKeyboardButton(left, callback_data=callback_data_left),
            InlineKeyboardButton(str(current_page) + '/' + str(all_pages), callback_data='Stop'),
            InlineKeyboardButton(right, callback_data=callback_data_right)
        ])

    buttons.append([InlineKeyboardButton('⬅️ Back to invoices statuses', callback_data='invoices_statuses')])

    return InlineKeyboardMarkup(buttons)


def invoice_details_keyboard(status, current_page) -> InlineKeyboardMarkup:
    button = [[InlineKeyboardButton('⬅️ Back to ' + status.lower() + ' invoices', callback_data='invoices_status_' + status + '_' + current_page)]]

    return InlineKeyboardMarkup(button)
