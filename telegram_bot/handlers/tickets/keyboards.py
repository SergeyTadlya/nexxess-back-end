from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def tickets_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('My tickets', callback_data='tickets_my')],
        [InlineKeyboardButton('Create ticket', callback_data='tickets_create')]
    ]

    return InlineKeyboardMarkup(buttons)


def tickets_statuses_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('Ongoing', callback_data='tickets_ongoing')],
        [InlineKeyboardButton('Overdue', callback_data='tickets_Overdue')],
        [InlineKeyboardButton('Closed', callback_data='tickets_Closed')],
        [InlineKeyboardButton('All', callback_data='tickets_All')],
        [InlineKeyboardButton('⬅️ Back to tickets menu', callback_data='tickets_menu')]
    ]

    return InlineKeyboardMarkup(buttons)


def all_tickets_keyboard(tickets) -> InlineKeyboardMarkup:
    buttons = list()

    for ticket in tickets:
        buttons.append([
            InlineKeyboardButton('#' + ticket.task_id + ' | ' + ticket.ticket_title, callback_data='tickets_detail_' + ticket.task_id)
        ])
    buttons.append([InlineKeyboardButton('⬅️ Back to tickets statuses', callback_data='tickets_my')])

    return InlineKeyboardMarkup(buttons)


def ticket_detail_keyboard() -> InlineKeyboardMarkup:
    buttons = [[InlineKeyboardButton('⬅️ Back to all tickets', callback_data='tickets_All')]]

    return InlineKeyboardMarkup(buttons)


def return_to_menu_keyboard() -> InlineKeyboardMarkup:
    button = [[InlineKeyboardButton('⬅️ Back to tickets menu', callback_data='tickets_menu')]]

    return InlineKeyboardMarkup(button)


def return_to_set_title_keyboard(ticket_id) -> InlineKeyboardMarkup:
    button = [[InlineKeyboardButton('⬅️ Change ticket title', callback_data='tickets_changeTitle_' + str(ticket_id))]]

    return InlineKeyboardMarkup(button)


# def return_to_set_description_keyboard(ticket_id) -> InlineKeyboardMarkup:
#     button = [[InlineKeyboardButton('⬅️ Change ticket description', callback_data='tickets_changeDescription_' + ticket_id)]]
#
#     return InlineKeyboardMarkup(button)
