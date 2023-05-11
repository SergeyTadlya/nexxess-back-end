from django.shortcuts import render, redirect
from tickets.models import Ticket
from invoices.models import Invoice
import requests
from authentication.helpers.B24Webhook import set_webhook
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView




class TestView(TemplateView):
    template_name = 'test.html'

@login_required(login_url='/accounts/login/')
def main(request):
    try:
        if request.user.is_superuser:
            invoice_count = Invoice.objects.filter(is_opened=False).count()
            task_count = Ticket.objects.filter(is_opened=False).count()
            current_user = "admin"
        else:
            invoice_count = Invoice.objects.filter(responsible=request.user.b24_contact_id, is_opened=False).count()
            task_count = Ticket.objects.filter(responsible=request.user.b24_contact_id, is_opened=False).count()
            current_user = "not_admin"

        method = "crm.product.list"
        url = set_webhook(method)
        product_count = requests.get(url).json()['total']

        res = {
            'invoice_count': invoice_count,
            'task_count': task_count,
            'services_all_count': product_count,
            'current_user': current_user
        }
    except:
        res = {
            'invoice_count': "0",
            'task_count': "0",
            'services_all_count': "0",
            # 'current_user': current_user
        }
    return render(request, "main.html", res)
