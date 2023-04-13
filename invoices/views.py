from django.shortcuts import render, redirect
from .models import Invoice


def invoices(request):
    # відфільтровуємо дані по пошті авторизованого користувачі (адміну будуть виводитись всі)
    if request.user.is_superuser:
        invoices_list = Invoice.objects.all()
    else:
        invoices_list = Invoice.objects.filter(responsible=request.user.email)

    arInvoice = []
    for invoice in invoices_list:
        arInvoice.append({
            'id': invoice.id,
            'invoice_id': invoice.invoice_id,
            'responsible': invoice.responsible,
            'is_opened': invoice.is_opened,
            'price': invoice.price,
        })
    res = {
        "invoices": arInvoice
    }
    return render(request, "invoices/invoices.html", res)


def invoice_detail(request, id):
    invoice = Invoice.objects.get(id=id)
    if request.user.is_superuser or invoice.responsible == request.user.email:
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