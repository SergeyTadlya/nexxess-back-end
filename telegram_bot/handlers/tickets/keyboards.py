from telegram import InlineKeyboardMarkup, InlineKeyboardButton


def tickets_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('My tickets', callback_data='tickets_my')],
        [InlineKeyboardButton('Create ticket', callback_data='tickets_create')]
    ]

    return InlineKeyboardMarkup(buttons)


def tickets_statuses_keyboard(tickets, tickets_statuses) -> InlineKeyboardMarkup:
    buttons = []

    for ticket_status in tickets_statuses:
        text = ticket_status.sticker + ' ' + ticket_status.name + ' (' + str(tickets.filter(status__name=ticket_status.name).count()) + ')'
        callback_data = 'tickets_status_' + ticket_status.name + '_1'

        buttons.append([InlineKeyboardButton(text, callback_data=callback_data)])

    buttons.append([InlineKeyboardButton('All tickets (' + str(len(tickets)) + ')', callback_data='tickets_status_All_1')])
    buttons.append([InlineKeyboardButton('⬅️ Back to tickets menu', callback_data='tickets_menu')])

    return InlineKeyboardMarkup(buttons)


def all_tickets_keyboard(tickets, current_page, all_pages, has_pages) -> InlineKeyboardMarkup:
    buttons = list()

    for ticket in tickets:
        ticket_detail = ticket.status.sticker + ' #' + ticket.task_id + ' | ' + ticket.ticket_title
        ticket_callback_data = 'tickets_status_All_' + str(current_page) + '_detail_' + ticket.task_id

        buttons.append([InlineKeyboardButton(ticket_detail, callback_data=ticket_callback_data)])

    if has_pages:
        callback_data_right = 'tickets_status_All_' + str(current_page - 1) if not current_page == 1 else 'Stop'
        callback_data_left = 'tickets_status_All_' + str(current_page + 1) if not current_page == all_pages else 'Stop'
        right = '⬅️' if not current_page == 1 else '🚫'
        left = '➡️' if not current_page == all_pages else '🚫'

        buttons.append([
            InlineKeyboardButton(right, callback_data=callback_data_right),
            InlineKeyboardButton(str(current_page) + '/' + str(all_pages), callback_data='Stop'),
            InlineKeyboardButton(left, callback_data=callback_data_left)
        ])

    buttons.append([InlineKeyboardButton('⬅️ Back to tickets statuses', callback_data='tickets_my')])

    return InlineKeyboardMarkup(buttons)


def tickets_for_selected_status_keyboard(tickets, status, current_page, all_pages, has_pages=False) -> InlineKeyboardMarkup:
    buttons = list()

    for ticket in tickets:
        ticket_detail = '#' + ticket.task_id + ' | ' + ticket.ticket_title
        ticket_callback_data = 'tickets_status_' + status.name + '_' + str(current_page) + '_detail_' + ticket.task_id

        buttons.append([InlineKeyboardButton(ticket_detail, callback_data=ticket_callback_data)])

    if has_pages:
        callback_data_right = 'tickets_status_' + status.name + '_' + str(current_page - 1) if not current_page == 1 else 'Stop'
        callback_data_left = 'tickets_status_' + status.name + '_' + str(current_page + 1) if not current_page == all_pages else 'Stop'
        right = '⬅️' if not current_page == 1 else '🚫'
        left = '➡️' if not current_page == all_pages else '🚫'

        buttons.append([
            InlineKeyboardButton(right, callback_data=callback_data_right),
            InlineKeyboardButton(str(current_page) + '/' + str(all_pages), callback_data='Stop'),
            InlineKeyboardButton(left, callback_data=callback_data_left)
        ])

    buttons.append([InlineKeyboardButton('⬅️ Back to tickets statuses', callback_data='tickets_my')])

    return InlineKeyboardMarkup(buttons)


def ticket_detail_keyboard(status_name, current_page) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton('⬅️ Back to ' + status_name.lower() + ' tickets', callback_data='tickets_status_' + status_name + '_' + current_page)],
        [InlineKeyboardButton('⏪ Back to tickets menu', callback_data='tickets_menu')]
    ]

    return InlineKeyboardMarkup(buttons)


def return_to_menu_keyboard() -> InlineKeyboardMarkup:
    button = [[InlineKeyboardButton('⬅️ Back to tickets menu', callback_data='tickets_menu')]]

    return InlineKeyboardMarkup(button)
