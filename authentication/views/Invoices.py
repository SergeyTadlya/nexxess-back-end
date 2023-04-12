from django.shortcuts import render, redirect
from authentication.models import Invoice
from datetime import datetime


def format_date(date_str):
    if date_str:
        date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
        return date_obj.strftime('%d %b %Y')
    else:
        return ''


def format_price(price):
    if '.' in str(price):
        price = str(price).rstrip('0').rstrip('.')
    else:
        price = str(price)
    return f'{price}$' if price else ''


def invoices(request):
    # відфільтровуємо дані по пошті авторизованого користувачі (адміну будуть виводитись всі)
    if request.user.is_superuser:
        invoices_list = Invoice.objects.all()
    else:
        invoices_list = Invoice.objects.filter(manager=request.user.email)

    arInvoice = []
    for invoice in invoices_list:

        arInvoice.append({
            'id': invoice.id,
            'invoice_id': invoice.invoice_id,
            'responsible': invoice.manager,
            'is_opened': invoice.is_opened,
            'price': format_price(invoice.price) if invoice.price else '',
            'date': format_date(invoice.date),
            'due_date': format_date(invoice.due_date),
            'status': invoice.status,
        })
    print('arInvoice', arInvoice)
    res = {
        "invoices": arInvoice
    }
    return render(request, "invoices/invoices.html", res)


def invoice_detail(request, id):
    responsible = Invoice.objects.get(id=id)
    if request.user.is_superuser or responsible.manager == request.user.email:
        # апдейт інвойса, коли менеджер відкрив її (це щоб на головній сторінці, вона зникла із списка нових задач)
        if not request.user.is_superuser:
            Invoice.objects.filter(id=id).update(is_opened=True)
        invoice = Invoice.objects.get(id=id)
        res = {
            'invoice': invoice,
        }
        return render(request, "invoices/detail.html", res)
    else:
        return redirect('/invoices/')
