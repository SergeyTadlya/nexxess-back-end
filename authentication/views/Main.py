from django.shortcuts import render, redirect
from tickets.models import Ticket
from invoices.models import Invoice
import requests
from authentication.helpers.B24Webhook import B24_WEBHOOK


def main(request):
    if not request.user.is_authenticated:
        return redirect("/accounts/login/")
    else:
        # виведення інформації про новий інвойс чи нову задачу, який отримав вебхук бітрікса
        # відфільтровуємо дані по пошті авторизованого користувачі (адміну будуть виводитись всі)
        if request.user.is_superuser:
            invoice_count = Invoice.objects.filter(is_opened=False).count()
            task_count = Ticket.objects.filter(is_opened=False).count()
            current_user = "admin"
        else:
            invoice_count = Invoice.objects.filter(responsible=request.user.email, is_opened=False).count()
            task_count = Ticket.objects.filter(responsible=request.user.email, is_opened=False).count()
            current_user = "not_admin"

        method = "crm.product.list"
        url = B24_WEBHOOK + method
        # product_count = requests.get(url).json()['total']

        res = {
            'invoice_count': invoice_count,
            'task_count': task_count,
            # 'services_all_count': product_count,
            'current_user': current_user
        }
        return render(request, "main.html", res)