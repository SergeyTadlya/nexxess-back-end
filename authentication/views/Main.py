from django.shortcuts import render, redirect
from tickets.models import Ticket, TicketStatus
from invoices.models import Invoice


import requests
from authentication.helpers.B24Webhook import set_webhook
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView




class TestView(TemplateView):
    template_name = 'test.html'

@login_required(login_url='/accounts/login/')
def main(request):
    # tasks_statuses = tasks(request).context.get('tasks_statuses', [])

    try:
        if request.user.is_superuser:
            invoice_count = Invoice.objects.all().exclude(status__value='Opened').count()
            task_count = Ticket.objects.filter(is_opened=False).count()
            current_user = "admin"
            status_closed = Ticket.objects.filter(status__name='Closed').count()
            status_overdue = Ticket.objects.filter(status__name='Overdue').count()
            status_ongoin = Ticket.objects.filter(tatus__name='Ongoing').count()

        else:
            invoice_count = Invoice.objects.filter(responsible=request.user.b24_contact_id).exclude(status__value='Paid').count()
            task_count = Ticket.objects.filter(responsible=str(request.user.b24_contact_id), is_opened=False).count()
            current_user = "not_admin"
            ticket_statuses = TicketStatus.objects.filter(ticket__responsible=str(request.user.b24_contact_id)).distinct()
            b_services = Invoice.objects.filter(responsible=request.user.b24_contact_id).exclude(status__value='Opened').count()
            status_closed = Ticket.objects.filter(responsible=str(request.user.b24_contact_id),  status__name='Closed').count()
            status_overdue = Ticket.objects.filter(responsible=str(request.user.b24_contact_id),  status__name='Overdue').count()
            status_ongoin = Ticket.objects.filter(responsible=str(request.user.b24_contact_id),  status__name='Ongoing').count()
            # print('ticket_statuses>>>>> count', ticket_statuses.count)
            print('status_closed>>>>>>', type(status_closed), status_closed)
            print('status_ongoing>>>>>>', type(status_overdue), status_overdue)
            print('status_ongoing>>>>>>', type(status_ongoin), status_ongoin)

        method = "crm.product.list"
        url = set_webhook(method)
        product_count = requests.get(url).json()['total']
        print('ticket_statuses.count>>>>>>>', ticket_statuses.count)
        res = {
            'invoice_count': invoice_count,
            'task_count': task_count,
            'services_all_count': product_count,
            'current_user': current_user,
            'ticket_statuses': ticket_statuses,
            'b_services': b_services,
            'status_closed': status_closed,
            'status_overdue': status_overdue,
            'status_ongoin': status_ongoin,


        }

    except:
        res = {
            'invoice_count': "0",
            'task_count': "0",
            'services_all_count': "0",
            # 'status_closed': '0',
            # 'status_overdue': '0',
            # 'status_ongoin': '0',

        }
    return render(request, "main.html", res)
