from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from datetime import date

from authentication.helpers.B24Webhook import set_webhook
from invoices.views import format_date
from tickets.models import Ticket, TelegramTicket

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

        elif callback_title == 'Ongoing':
            self.show_ongoing_tickets()

        elif callback_title == 'Overdue':
            self.show_overdue_tickets()

        elif callback_title == 'Closed':
            self.show_closed_tickets()

        elif callback_title == 'All':
            self.show_all_tickets()

        elif 'detail' in callback_title:
            ticket_id = callback_title.split('_')[1]

            self.show_ticket_details(ticket_id)

        elif callback_title == 'create':
            self.show_set_ticket_title()

        # elif callback_title == 'changeTitle':
        #     ticket_id = callback_title.split('_')[2]
        #     self.save_ticket_title(ticket_id)

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

            user.step = ''
            user.save()

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
        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text='Choose tickets status',
                             reply_markup=tickets_statuses_keyboard())

    def show_ongoing_tickets(self):
        user = get_user(self.data['callback_query'])
        tickets = Ticket.objects.filter(responsible=user.email, filter='Ongoing')

        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text='All tickets for ' + user.email)

    def show_overdue_tickets(self):
        user = get_user(self.data['callback_query'])
        tickets = Ticket.objects.filter(responsible=user.email, status='Overdue')

        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text='All tickets for ' + user.email)

    def show_closed_tickets(self):
        user = get_user(self.data['callback_query'])
        tickets = Ticket.objects.filter(responsible=user.email, status='Closed')

        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text='All tickets for ' + user.email)

    def show_all_tickets(self):
        user = get_user(self.data['callback_query'])
        tickets = Ticket.objects.filter(responsible=user.b24_contact_id)

        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text='All tickets for ' + user.email,
                             reply_markup=all_tickets_keyboard(tickets))

    def show_ticket_details(self, ticket_id):
        ticket = Ticket.objects.filter(task_id=ticket_id)
        if ticket.exists():
            ticket = ticket.first()

        open_value = '☑️\n' if ticket.is_opened is True else '❌\n'
        active_value = '☑️' if ticket.is_active is True else '❌'

        ticket_detail = 'Ticket title (#' + ticket_id + '): \n' + \
                        ticket.ticket_title + '\n\n' + \
                        'Description: \n' + ticket.ticket_text + '\n\n' + \
                        'Status: ' + str(ticket.status) + '\n' + \
                        'Deadline: ' + format_date(ticket.deadline) + '\n' + \
                        'Open: ' + open_value + \
                        'Active: ' + active_value

        self.bot.sendMessage(chat_id=get_chat_id(self.data['callback_query']),
                             text=ticket_detail,
                             reply_markup=ticket_detail_keyboard())

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

        calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today()).build()
        self.bot.sendMessage(chat_id=get_chat_id(self.data),
                             text=f'Okay, it remains to choose the deadline\n'
                                  f'Select {LSTEP[step]}  for deadline:',
                             reply_markup=calendar)
