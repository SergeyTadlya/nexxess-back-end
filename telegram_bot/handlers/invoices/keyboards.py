from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from invoices.views import format_date, format_price


def invoices_statuses_keyboard(invoices) -> InlineKeyboardMarkup:

    buttons = [
        [InlineKeyboardButton(f'🔵 New ({invoices["new"]})', callback_data='invoices_New')],
        [InlineKeyboardButton(f'🟢 Paid ({invoices["paid"]})', callback_data='invoices_Paid')],
        [InlineKeyboardButton(f'🟡 Unpaid ({invoices["unpaid"]})', callback_data='invoices_Unpaid')],
        [InlineKeyboardButton(f'All invoices ({invoices["all"]})', callback_data='invoices_All')]
    ]
    return InlineKeyboardMarkup(buttons)


def new_invoices_keyboard(new_invoices, current_page, all_pages, has_pages) -> InlineKeyboardMarkup:

    buttons = []

    for new_invoice in new_invoices:
        buttons.append(
            [
                InlineKeyboardButton(
                    f'ID: #{new_invoice.invoice_id} | Price: {format_price(new_invoice.price)} | Date: {format_date(new_invoice.date)}',
                    callback_data=f'invoices_id_{new_invoice.invoice_id}'
                )
            ]
        )
    if has_pages:
        buttons.append(
            [InlineKeyboardButton(
                '⬅️' if not current_page == 1 else '🚫',
                callback_data=f'invoices_New_previous_{current_page - 1}' if not current_page == 1 else 'Stop'
            ),
             InlineKeyboardButton(
                 f'{current_page} / {all_pages}',
                 callback_data=f'current_page'
             ),
             InlineKeyboardButton(
                 '➡️' if not current_page == all_pages else '🚫',
                 callback_data=f'invoices_New_next_{current_page + 1}' if not current_page == all_pages else 'Stop'
             )]
        )
    buttons.append([InlineKeyboardButton('⬅️ Back to statuses', callback_data='invoices_statuses')])

    return InlineKeyboardMarkup(buttons)


def paid_invoices_keyboard(paid_invoices, current_page, all_pages, has_pages) -> InlineKeyboardMarkup:

    buttons = []

    for paid_invoice in paid_invoices:
        buttons.append(
            [
                InlineKeyboardButton(
                    f'ID: #{paid_invoice.invoice_id} | Price: {format_price(paid_invoice.price)} | Date: {format_date(paid_invoice.date)}',
                    callback_data=f'invoices_id_{paid_invoice.invoice_id}'
                )
            ]
        )
    if has_pages:
        buttons.append(
            [InlineKeyboardButton(
                '⬅️' if not current_page == 1 else '🚫',
                callback_data=f'invoices_Paid_previous_{current_page - 1}' if not current_page == 1 else 'Stop'
            ),
             InlineKeyboardButton(
                 f'{current_page} / {all_pages}',
                 callback_data=f'current_page'
             ),
             InlineKeyboardButton(
                 '➡️' if not current_page == all_pages else '🚫',
                 callback_data=f'invoices_Paid_next_{current_page + 1}' if not current_page == all_pages else 'Stop'
             )]
        )
    buttons.append([InlineKeyboardButton('⬅️ Back to statuses', callback_data='invoices_statuses')])

    return InlineKeyboardMarkup(buttons)


def unpaid_invoices_keyboard(unpaid_invoices, current_page, all_pages, has_pages) -> InlineKeyboardMarkup:

    buttons = []

    for unpaid_invoice in unpaid_invoices:
        buttons.append(
            [
                InlineKeyboardButton(
                    f'ID: #{unpaid_invoice.invoice_id} | Price: {format_price(unpaid_invoice.price)} | Date: {format_date(unpaid_invoice.date)}',
                    callback_data=f'invoices_id_{unpaid_invoice.invoice_id}'
                )
            ]
        )
    if has_pages:
        buttons.append(
            [InlineKeyboardButton(
                '⬅️' if not current_page == 1 else '🚫',
                callback_data=f'invoices_Unpaid_previous_{current_page - 1}' if not current_page == 1 else 'Stop'
            ),
             InlineKeyboardButton(
                 f'{current_page} / {all_pages}',
                 callback_data=f'current_page'
             ),
             InlineKeyboardButton(
                 '➡️' if not current_page == all_pages else '🚫',
                 callback_data=f'invoices_Unpaid_next_{current_page + 1}' if not current_page == all_pages else 'Stop'
             )]
        )
    buttons.append([InlineKeyboardButton('⬅️ Back to statuses', callback_data='invoices_statuses')])

    return InlineKeyboardMarkup(buttons)


def all_invoices_keyboard(all_invoices, current_page, all_pages, has_pages) -> InlineKeyboardMarkup:

    buttons = []

    for invoice in all_invoices:
        buttons.append(
            [
                InlineKeyboardButton(
                    f'ID: #{invoice.invoice_id} | Price: {format_price(invoice.price)} | Date: {format_date(invoice.date)}',
                    callback_data=f'invoices_id_{invoice.invoice_id}'
                )
            ]
        )
    if has_pages:
        buttons.append(
            [InlineKeyboardButton(
                '⬅️' if not current_page == 1 else '🚫',
                callback_data=f'invoices_All_previous_{current_page - 1}' if not current_page == 1 else 'Stop'
            ),
             InlineKeyboardButton(
                 f'{current_page} / {all_pages}',
                 callback_data=f'current_page'
             ),
             InlineKeyboardButton(
                 '➡️' if not current_page == all_pages else '🚫',
                 callback_data=f'invoices_All_next_{current_page + 1}' if not current_page == all_pages else 'Stop'
             )]
        )
    buttons.append([InlineKeyboardButton('⬅️ Back to statuses', callback_data='invoices_statuses')])

    return InlineKeyboardMarkup(buttons)
