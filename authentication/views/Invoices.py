from django.shortcuts import render, redirect
from authentication.models import Invoice


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
        })
    print('arInvoice', arInvoice)
    res = {
        "invoices": arInvoice
    }
    return render(request, "invoices/list.html", res)


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