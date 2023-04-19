from .models import Invoice
from django.shortcuts import render, redirect
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from datetime import datetime


def format_date(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z').strftime('%d %b %Y')if date_str else ''


def format_price(price):
    price = str(price)
    price = price.rstrip('0').rstrip('.') if '.' in price else price

    return f'${price}' if price else ''


def invoices(request):
    # відфільтровуємо дані по пошті авторизованого користувачі (адміну будуть виводитись всі)
    all_user_invoices = Invoice.objects.all() if request.user.is_superuser \
                   else Invoice.objects.filter(responsible=request.user.email)

    invoices_array = list()
    invoices_dates = list()

    for invoice in all_user_invoices:
        invoices_array.append({
            'id': invoice.id,
            'invoice_id': invoice.invoice_id,
            'responsible': invoice.responsible,
            'is_opened': invoice.is_opened,
            'price': format_price(invoice.price),
            'date': format_date(invoice.date),
            'due_date': format_date(invoice.due_date),
            'status': invoice.status,
        })

        if format_date(invoice.date) not in invoices_dates:
            invoices_dates.append(format_date(invoice.date))

    context = {
        "invoices": invoices_array,
        "invoices_dates": invoices_dates.sort()
    }
    return render(request, "invoices/invoices.html", context)


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


def create_invoice_pdf(request, id):
    invoice = Invoice.objects.get(id=id)

    if request.user.is_superuser or invoice.responsible == request.user.email:

        context = {'invoice': invoice}

        template = get_template('invoices/pdf_template.html')
        html = template.render(context)

        pdf_file = BytesIO()
        pisa.CreatePDF(BytesIO(html.encode('utf-8')), pdf_file)

        response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename=invoice_{id}.pdf'
        return response

    else:
        return redirect('/invoices/')
