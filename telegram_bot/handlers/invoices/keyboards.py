from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from invoices.views import format_date, format_price


def invoices_statuses_keyboard(invoices, invoices_statuses) -> InlineKeyboardMarkup:
    buttons = []

    for invoice_status in invoices_statuses:
        text = f'{invoice_status.sticker} {invoice_status.value} ({invoices.filter(status__value=invoice_status.value).count()})'
        callback_data = f'invoices_status_{invoice_status.value}_1'

        buttons.append([InlineKeyboardButton(text, callback_data=callback_data)])

    buttons.append([InlineKeyboardButton(f'All invoices ({len(invoices)})', callback_data='invoices_status_All_1')])

    return InlineKeyboardMarkup(buttons)


def invoices_for_selected_status_keyboard(invoices, status, current_page, all_pages, has_pages):
    buttons = list()

    for invoice in invoices:
        sticker = invoice.status.sticker
        product_title_preview = invoice.product_title if len(invoice.product_title) < 18 else invoice.product_title[:18] + '...'
        price = format_price(invoice.price)
        date = format_date(invoice.date)

        invoice_detail = f'{sticker} {product_title_preview} | {price} | {date}'
        invoice_callback_data = f'invoices_status_{status.value}_{current_page}_detail_{invoice.invoice_id}'

        buttons.append([InlineKeyboardButton(invoice_detail, callback_data=invoice_callback_data)])

    if has_pages:
        callback_data_right = f'invoices_status_{status.value}_{current_page - 1}' if not current_page == 1 else 'Stop'
        callback_data_left = f'invoices_status_{status.value}_{current_page + 1}' if not current_page == all_pages else 'Stop'
        right = '➡️' if not current_page == all_pages else '🚫'
        left = '⬅️' if not current_page == 1 else '🚫'

        buttons.append([
            InlineKeyboardButton(left, callback_data=callback_data_right),
            InlineKeyboardButton(f'{current_page} / {all_pages}', callback_data='Stop'),
            InlineKeyboardButton(right, callback_data=callback_data_left)
        ])

    buttons.append([InlineKeyboardButton('⬅️ Back to invoices statuses', callback_data='invoices_statuses')])

    return InlineKeyboardMarkup(buttons)


def all_invoices_keyboard(invoices, current_page, all_pages, has_pages) -> InlineKeyboardMarkup:
    buttons = list()

    for invoice in invoices:
        sticker = invoice.status.sticker
        product_title_preview = invoice.product_title if len(invoice.product_title) < 18 else invoice.product_title[:18] + '...'
        price = format_price(invoice.price)
        date = format_date(invoice.date)

        invoice_detail = f'{sticker} {product_title_preview} | {price} | {date}'
        invoice_callback_data = f'invoices_status_All_{current_page}_detail_{invoice.invoice_id}'

        buttons.append([InlineKeyboardButton(invoice_detail, callback_data=invoice_callback_data)])

    if has_pages:
        callback_data_left = 'invoices_status_All_' + str(current_page - 1) if not current_page == 1 else 'Stop'
        callback_data_right = 'invoices_status_All_' + str(current_page + 1) if not current_page == all_pages else 'Stop'
        left = '⬅️' if not current_page == 1 else '🚫'
        right = '➡️' if not current_page == all_pages else '🚫'

        buttons.append([
            InlineKeyboardButton(left, callback_data=callback_data_left),
            InlineKeyboardButton(f'{current_page} / {all_pages}', callback_data='Stop'),
            InlineKeyboardButton(right, callback_data=callback_data_right)
        ])

    buttons.append([InlineKeyboardButton('⬅️ Back to invoices statuses', callback_data='invoices_statuses')])

    return InlineKeyboardMarkup(buttons)


def invoice_details_keyboard(status, current_page, invoice) -> InlineKeyboardMarkup:
    if invoice.status.value == 'Paid':
        buttons = [
            [InlineKeyboardButton(f'⬅️ Back to {status.lower()} invoices', callback_data=f'invoices_status_{status}_{current_page}')]
        ]
    else:
        buttons = [
            [InlineKeyboardButton('Pay the invoice', callback_data='services_detail_' + invoice.invoice_id)],
            [InlineKeyboardButton(f'⬅️ Back to {status.lower()} invoices', callback_data=f'invoices_status_{status}_{current_page}')]
        ]
    return InlineKeyboardMarkup(buttons)
