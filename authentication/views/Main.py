from django.shortcuts import render, redirect
from authentication.models import Ticket, Invoice
import requests
import json


def main(request):
    if not request.user.is_authenticated:
        return redirect("/accounts/login/")
    else:
        # виведення інформації про новий інвойс чи нову задачу, який отримав вебхук бітрікса
        # відфільтровуємо дані по пошті авторизованого користувачі (адміну будуть виводитись всі)
        if request.user.is_superuser:
            invoice_count = Invoice.objects.filter(is_opened=False).count()
            task_count = Ticket.objects.filter(is_opened=False).count()
        else:
            invoice_count = Invoice.objects.filter(responsible=request.user.email, is_opened=False).count()
            task_count = Ticket.objects.filter(responsible=request.user.email, is_opened=False).count()

        res = {
            'invoice_count': invoice_count,
            'task_count': task_count,
        }
        return render(request, "main.html", res)