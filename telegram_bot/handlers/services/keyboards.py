from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from invoices.views import format_date, format_price


def services_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('My services', callback_data='services_my')],
        [InlineKeyboardButton('All services', callback_data='services_all')]
    ]
    return InlineKeyboardMarkup(buttons)


def user_services_keyboard(user_services) -> InlineKeyboardMarkup:
    buttons = list()
    for service in user_services:
        service_text = '📚 ' + service.title if service.category.category_name == 'Books' else '📦 ' + service.title
        service_callback_data = 'services_detailMy_' + service.service_id

        buttons.append([InlineKeyboardButton(service_text, callback_data=service_callback_data)])
    buttons.append([InlineKeyboardButton('⬅️ Back to services menu', callback_data='services_menu')])

    return InlineKeyboardMarkup(buttons)


def back_to_my_services_keyboard() -> InlineKeyboardMarkup:
    button = [[InlineKeyboardButton('⬅️ Back to my services', callback_data='services_my')]]

    return InlineKeyboardMarkup(button)


def all_services_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('📚 Nexxess trust books', callback_data='services_ctg_B')],
        [InlineKeyboardButton('📦 Nexxess packages', callback_data='services_ctg_P')],
        [InlineKeyboardButton('⬅️ Back to services menu', callback_data='services_menu')]
    ]

    return InlineKeyboardMarkup(buttons)


def selected_category_keyboard(services) -> InlineKeyboardMarkup:
    buttons = list()

    for service in services:
        service_text = f'{service.title} - {format_price(service.price)}'
        service_callback_data = 'services_info_' + service.service_id

        buttons.append([InlineKeyboardButton(service_text, callback_data=service_callback_data)])
    buttons.append([InlineKeyboardButton('⬅️ Back to services category', callback_data='services_all')])

    return InlineKeyboardMarkup(buttons)


def service_info_keyboard(service, more_one) -> InlineKeyboardMarkup:
    buttons = list()
    if more_one:
        buttons.append(
            [InlineKeyboardButton('⬅️ Choose another', callback_data='services_ctg_' + service.category.category_name[0]),
             InlineKeyboardButton('Order', callback_data=f'services_order_{service.service_id}')]
        )
    else:
        buttons.append([InlineKeyboardButton('Order', callback_data=f'services_order_{service.service_id}')])

    buttons.append([InlineKeyboardButton('⏪ Back to services category', callback_data='services_all')])

    return InlineKeyboardMarkup(buttons)


def already_existing_service_keyboard(invoice) -> InlineKeyboardMarkup:
    sticker = invoice.status.sticker
    product_title_preview = invoice.product_title if len(invoice.product_title) < 17 else invoice.product_title[:17] + '...'
    price = format_price(invoice.price)
    date = format_date(invoice.date)

    button = [[
        InlineKeyboardButton(
            f'{sticker} {product_title_preview} | {price} | {date}',
            callback_data='services_detail_' + invoice.invoice_id)
    ]]
    return InlineKeyboardMarkup(button)


def invoice_for_selected_service_keyboard(service, invoice=None) -> InlineKeyboardMarkup:
    if invoice is None:
        buttons = [
            [InlineKeyboardButton(f'Pay {format_price(service.price)}.00', pay=True)],
            [InlineKeyboardButton('⬅️ Back to ' + service.title, callback_data=f'services_info_{service.service_id}_del')]
        ]

    elif invoice.status.value == 'Paid':
        buttons = [
            [InlineKeyboardButton('⬅️ Back to ' + service.title, callback_data=f'services_info_{service.service_id}_del')]
        ]

    else:
        buttons = [
            [InlineKeyboardButton(f'Pay {format_price(service.price)}.00', pay=True)],
            [InlineKeyboardButton('⬅️ Back to ' + service.title,
                                  callback_data=f'services_info_{service.service_id}_del')]
        ]

    return InlineKeyboardMarkup(buttons)

