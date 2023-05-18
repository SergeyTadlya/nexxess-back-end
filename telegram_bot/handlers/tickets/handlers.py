from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date

from authentication.helpers.B24Webhook import set_webhook
from invoices.views import format_date
from tickets.models import Ticket, TelegramTicket, TicketStatus

from .keyboards import *
from ..utils import *

import requests


class TicketsHandler:
    def __init__(self, bot, data, callback_title):
        self.bot = bot
        self.data = data

        callback_title = callback_title.replace('tickets_', '')

        if callback_title == 'menu':
            self.show_tickets_menu(self.bot, self.data['callback_query'])

        elif callback_title == 'my':
            self.show_tickets_statuses()

        elif 'detail' in callback_title:
            parsed_data = callback_title.split('_')
            status_name = parsed_data[1]
            current_page = parsed_data[2]
            ticket_id = parsed_data[4]

            self.show_ticket_details(status_name, current_page, ticket_id)

        elif 'status_All' in callback_title:
            parsed_data = callback_title.split('_')
            current_page = int(parsed_data[2])

            self.show_all_tickets(current_page)

        elif 'status_' in callback_title:
            parsed_data = callback_title.split('_')
            status_name = parsed_data[1]
            current_page = int(parsed_data[2])

            self.show_ticket_for_selected_status(status_name, current_page)

        elif callback_title == 'create':
            self.show_set_ticket_title()

    @staticmethod
    def create_new_ticket(bot, data, deadline):
        user = get_user(data['callback_query'])
        telegram_ticket = TelegramTicket.objects.filter(responsible=str(user.email))

        if telegram_ticket.exists():
            telegram_ticket = telegram_ticket.first()

        # Ticket webhook
        url = set_webhook("tasks.task.add")

        payload = {
            'fields': {
                'TITLE': telegram_ticket.title,
                'DESCRIPTION': telegram_ticket.description,
                'DEADLINE': deadline,
                'CREATED_BY': 2,
                'RESPONSIBLE_ID': 1,
                'PRIORITY': 2,
                'ALLOW_CHANGE_DEADLINE': 1,
                'UF_CRM_TASK': {
                    "0": 'C_' + str(user.b24_contact_id),  # bitrix24_id
                }
            }
        }
        response = requests.post(url, json=payload)

        if response.status_code == 200:
            TelegramTicket.objects.filter(responsible=user.email).delete()

            bot.sendMessage(chat_id=get_chat_id(data['callback_query']),
                            text='Great, ticket successfully created',
                            reply_markup=return_to_menu_keyboard())

    @staticmethod
    def show_tickets_menu(bot, data):
        user = get_user(data)
        TelegramTicket.objects.filter(responsible=user.email).delete()
        user.step = ''
        user.save()

        bot.sendMessage(chat_id=get_chat_id(data),
                        text='Choose options',
                        reply_markup=tickets_menu_keyboard())

    def show_tickets_statuses(self):
        user = get_user(self.data['callback_query'])
        tickets_statuses = TicketStatus.objects.all()
        tickets = Ticket.objects.filter(responsible=str(user.b24_contact_id)).order_by('-created_at')

        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text='Choose the ticket status',
                             reply_markup=tickets_statuses_keyboard(tickets, tickets_statuses))

    def show_ticket_for_selected_status(self, status_name, current_page, element_on_page=8):
        user = get_user(self.data['callback_query'])
        ticket_status = TicketStatus.objects.get(name=status_name)
        tickets = Ticket.objects.filter(responsible=str(user.b24_contact_id), status=ticket_status).order_by('-created_at')

        tickets_quantity = len(tickets)
        if tickets_quantity == 0:
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text='You don`t have any ' + status_name.lower() + ' tickets')
            return

        all_pages = tickets_quantity // element_on_page if not tickets_quantity % element_on_page else (tickets_quantity // element_on_page) + 1
        has_pages = False

        if tickets_quantity > element_on_page:
            has_pages = True
            tickets = tickets[element_on_page * (current_page - 1):element_on_page*current_page]

        try:
            message = ticket_status.sticker + ' ' + ticket_status.name + ' tickets: '
            self.bot.edit_message_text(
                message,
                chat_id=get_chat_id(self.data['callback_query']),
                message_id=self.data['callback_query']['message']['message_id'],
                reply_markup=tickets_for_selected_status_keyboard(tickets, ticket_status, current_page, all_pages, has_pages)
            )
        except Exception as e:
            print(e)

    def show_all_tickets(self, current_page, element_on_page=8):
        user = get_user(self.data['callback_query'])
        tickets = Ticket.objects.filter(responsible=user.b24_contact_id).order_by('created_at')

        tickets_quantity = len(tickets)
        if tickets_quantity == 0:
            self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                                 text='You don`t have any tickets')
            return

        all_pages = tickets_quantity // element_on_page if not tickets_quantity % element_on_page else (tickets_quantity // element_on_page) + 1
        has_pages = False

        if tickets_quantity > element_on_page:
            has_pages = True
            tickets = tickets[element_on_page * (current_page - 1):element_on_page * current_page]

        try:
            self.bot.edit_message_text(
                'All tickets: ',
                chat_id=get_chat_id(self.data['callback_query']),
                message_id=self.data['callback_query']['message']['message_id'],
                reply_markup=all_tickets_keyboard(tickets, current_page, all_pages, has_pages)
            )
        except Exception as e:
            print(e)

    def show_ticket_details(self, status_name, current_page, ticket_id):
        ticket = Ticket.objects.filter(task_id=ticket_id)
        if ticket.exists():
            ticket = ticket.first()

        active_value = '☑️' if ticket.is_active is True else '❌'

        ticket_detail = 'Ticket #' + ticket_id + '\n' + \
                        'Title: \n' + ticket.ticket_title + '\n\n' + \
                        'Description: \n' + ticket.ticket_text + '\n\n' + \
                        'Status: ' + str(ticket.status.name) + '\n' + \
                        'Deadline: ' + format_date(ticket.deadline) + '\n' + \
                        'Active: ' + active_value

        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text=ticket_detail,
                             reply_markup=ticket_detail_keyboard(status_name, current_page))

    def show_set_ticket_title(self):
        user = get_user(self.data['callback_query'])
        user.step = 'SET_TICKET_TITLE'
        user.save()

        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text='Enter a ticket title:',
                             reply_markup=return_to_menu_keyboard())

    def save_ticket_title(self, title):
        if title == 'None' or title.startswith('/') or title in ['👨‍💻 Services', '🧾 Invoices', '📝 Tickets', '⁉️ FAQ', '🚪 Log Out']:
            self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                 text='Only text format is accepted\n'
                                      'Try again:')
            return
        user = get_user(self.data)
        TelegramTicket.objects.create(responsible=user.email, title=title)
        user.step = 'SET_TICKET_DESCRIPTION'
        user.save()

        self.bot.sendMessage(chat_id=get_chat_id(self.data),
                             text='Great, now describe the situation:')
                            # reply_markup=return_to_set_title_keyboard(ticket.id)

    def save_ticket_description(self, description):
        if description == 'None' or description.startswith('/') or description in ['👨‍💻 Services', '🧾 Invoices', '📝 Tickets', '⁉️ FAQ', '🚪 Log Out']:
            self.bot.sendMessage(chat_id=get_chat_id(self.data),
                                 text='Only text format is accepted\n'
                                      'Try again:')
            return

        user = get_user(self.data)
        telegram_ticket = TelegramTicket.objects.filter(responsible=user.email)

        if telegram_ticket.exists():
            telegram_ticket = telegram_ticket.first()

        telegram_ticket.description = description
        telegram_ticket.save()

        user.step = ''
        user.save()

        calendar, step = MyStyleCalendar(calendar_id=1, min_date=date.today()).build()
        self.bot.sendMessage(chat_id=get_chat_id(self.data),
                             text=f'Okay, it remains to choose the deadline\n'
                                  f'Select {LSTEP[step]}  for deadline:',
                             reply_markup=calendar)
