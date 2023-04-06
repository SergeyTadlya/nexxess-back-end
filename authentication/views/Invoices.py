from django.shortcuts import render, redirect
from authentication.models import Invoice


def invoices(request):
    invoices = Invoice.objects.all()
    res = {
        "invoices": invoices
    }
    return render(request, "invoices/list.html", res)


def invoice_detail(request, id):
    invoice = Invoice.objects.get(id=id)
    res = {
        'invoice': invoice,
    }
    return render(request, "invoices/detail.html", res)