from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from invoices.views import format_date, format_price


def services_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('My services', callback_data='services_my')],
        [InlineKeyboardButton('All services', callback_data='services_all')]
    ]
    return InlineKeyboardMarkup(buttons)


def all_services_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('👥 Hourly rate chart for consultation', callback_data='services_ctg_C')],
        [InlineKeyboardButton('📚 Nexxess trust books', callback_data='services_ctg_B')],
        [InlineKeyboardButton('📦 Nexxess packages', callback_data='services_ctg_P')],
        [InlineKeyboardButton('⬅️ Back to services menu', callback_data='services_menu')]
    ]

    return InlineKeyboardMarkup(buttons)


def selected_category_keyboard(services, category_name) -> InlineKeyboardMarkup:
    buttons = list()

    for service in services:
        service_text = service.title + ' - ' + format_price(service.price)
        service_callback_data = 'services_detail_' + service.service_id

        buttons.append([InlineKeyboardButton(service_text, callback_data=service_callback_data)])
    buttons.append([InlineKeyboardButton('⬅️ Back to category menu', callback_data='services_all')])

    return InlineKeyboardMarkup(buttons)


def service_detail_keyboard(service) -> InlineKeyboardMarkup:
    button = [
        [InlineKeyboardButton('⬅️ Choose another', callback_data='services_ctg_' + service.category.category_name[0]),
         InlineKeyboardButton('Order', callback_data=f'services_order_{service.service_id}')],

        [InlineKeyboardButton('⏪ Back to services', callback_data='services_all')]
    ]

    return InlineKeyboardMarkup(button)
