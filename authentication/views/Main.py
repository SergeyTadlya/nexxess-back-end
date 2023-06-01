from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.shortcuts import render, redirect

from authentication.helpers.B24Webhook import set_webhook
from tickets.models import Ticket, TicketStatus
from invoices.models import Invoice

import requests


class TestView(TemplateView):
    template_name = 'test.html'


@login_required(login_url='/accounts/login/')
def main(request):
    try:
        if request.user.is_superuser:
            invoice_count = Invoice.objects.all().exclude(status__value='Opened').count()
            task_count = Ticket.objects.filter(is_opened=False).count()
            current_user = "admin"



        else:
            invoice_count = Invoice.objects.filter(responsible=request.user.b24_contact_id).exclude(status__value='Paid').exclude(status__value='Opened').count()
            task_count = Ticket.objects.filter(responsible=str(request.user.b24_contact_id), is_opened=False).count()
            current_user = "not_admin"
            ticket_statuses = TicketStatus.objects.filter(ticket__responsible=str(request.user.b24_contact_id)).distinct()
            b_services = Invoice.objects.filter(responsible=request.user.b24_contact_id).exclude(status__value='Opened').count()

            b_services = Invoice.objects.filter(responsible=request.user.b24_contact_id).exclude(status__value='Opened').exclude(status__value='New').count()

        method = "crm.product.list"
        url = set_webhook(method)
        product_count = requests.get(url).json()['total']



        all_user_tickets = Ticket.objects.all().order_by('-created_at') if request.user.is_superuser \
            else Ticket.objects.filter(responsible=request.user.b24_contact_id).order_by('-created_at')

        bought_services = Invoice.objects.filter(responsible=str(request.user.b24_contact_id), status__value='Paid')

        all_tickets_statuses = TicketStatus.objects.all()
        tickets_statuses = list()
        status_check = list()

        for ticket in all_user_tickets:
            for ticket_status in all_tickets_statuses:

                if ticket_status.name == ticket.status.name:
                    ticket_status_quantity = all_user_tickets.filter(status__name=ticket_status.name).count()

                    if ticket.status.name not in status_check:
                        status_check.append(ticket.status.name)
                        tickets_statuses.append({
                                        'name': ticket.status.name,
                                        'color': ticket.status.color,
                                        'number': ticket_status_quantity
                                        })

        res = {
            'invoice_count': invoice_count,
            'task_count': task_count,
            'services_all_count': product_count,
            'current_user': current_user,
            'ticket_statuses': ticket_statuses,
            'b_services': b_services,
            'statuses': tickets_statuses,

        }

    except:
        res = {
            'invoice_count': "0",
            'task_count': "0",
            'services_all_count': "0",
        }

    if request.user.is_superuser:
        return render(request, "main_superuser.html", res)

    else:
        return render(request, "main.html", res)
