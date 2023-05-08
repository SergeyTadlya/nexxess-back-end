from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from invoices.views import format_price


def services_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('My services', callback_data='services_my')],
        [InlineKeyboardButton('All services', callback_data='services_all')]
    ]
    return InlineKeyboardMarkup(buttons)


def all_services_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('Hourly rate chart for consultation', callback_data='tickets_consultations')],
        [InlineKeyboardButton('Nexxess trust books', callback_data='tickets_books')],
        [InlineKeyboardButton('Nexxess packages', callback_data='tickets_packages')],
        [InlineKeyboardButton('⬅️ Back to services menu', callback_data='services_menu')]
    ]

    return InlineKeyboardMarkup(buttons)


def service_detail_keyboard(service) -> InlineKeyboardMarkup:
    button = [
        [InlineKeyboardButton('Order', callback_data=f'services_order_{service.service_id}')],
        [InlineKeyboardButton('⬅️ Back to services', callback_data='services_all')]
    ]

    return InlineKeyboardMarkup(button)
