from django.template.loader import get_template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from datetime import datetime
from io import BytesIO
from django.contrib.auth.decorators import login_required
from .models import Invoice, Status

import xhtml2pdf.pisa as pisa
import json


def format_date(date):
    return date.strftime('%d %b %Y') if date else ''


def format_price(price):
    price = str(price)
    price = price.rstrip('0').rstrip('.') if '.' in price else price

    return f'${price}' if price else ''

@login_required(login_url='/accounts/login/')
def invoices(request):
  

    all_user_invoices = Invoice.objects.all().order_by('-date') if request.user.is_superuser \
        else Invoice.objects.filter(responsible=request.user.b24_contact_id).order_by('-date')

    invoices_array = list()
    invoices_dates = list()
    statuses_number = dict()
    invoices_statuses = list()

    for invoice in all_user_invoices:

        statuses_number[invoice.status.value] = 1 if invoice.status.value not in statuses_number.keys() \
            else statuses_number[invoice.status.value] + 1

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

    for index, (status_name, status_number) in enumerate(statuses_number.items()):
        invoices_statuses.append({
            'id': 'status' + str(index + 1),
            'name': status_name,
            'number': status_number
        })

    paginator = Paginator(invoices_array, 10)
    page = request.GET.get('page', 1)

    try:
        invoices_array = paginator.page(page)
    except PageNotAnInteger:
        invoices_array = paginator.page(1)
    except EmptyPage:
        invoices_array = paginator.page(paginator.num_pages)

    context = {
        "invoices": invoices_array,
        "invoices_dates": invoices_dates,
        'invoices_statuses': invoices_statuses,
        'statuses_amount': len(invoices_statuses),
        'invoices_number': len(all_user_invoices),
    }

    return render(request, "invoices/invoices.html", context)


def ajax_invoice_filter(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        if request.method == 'POST':
            data = json.load(request)
            statuses = [keys for keys in data if data[keys] is True]

            all_user_invoices = Invoice.objects.filter(responsible=request.user).order_by('-date')
            invoices_array = list()
            invoices_dates = list()

            if statuses:
                all_user_invoices = all_user_invoices.filter(status__value__in=statuses)

            if data['from_date'] and data['to_date']:
                all_user_invoices = all_user_invoices.filter(
                    date__gte=datetime.strptime(data['from_date'], '%B.%d.%Y'),
                    date__lte=datetime.strptime(data['to_date'], '%B.%d.%Y')
                )

            if data['local_search']:
                all_user_invoices = all_user_invoices.filter(
                    Q(invoice_id__icontains=data['local_search']) |
                    Q(price__icontains=data['local_search']) |
                    Q(status__value__icontains=data['local_search']) |
                    Q(date__icontains=data['local_search']) |
                    Q(due_date__icontains=data['local_search'])
                )

            for invoice in all_user_invoices:
                invoices_array.append({
                    'id': invoice.id,
                    'invoice_id': invoice.invoice_id,
                    'responsible': invoice.responsible,
                    'is_opened': invoice.is_opened,
                    'price': format_price(invoice.price),
                    'date': format_date(invoice.date),
                    'due_date': format_date(invoice.due_date),
                    'status_value': invoice.status.value,
                    'status_color': invoice.status.color
                })

                if format_date(invoice.date) not in invoices_dates:
                    invoices_dates.append(format_date(invoice.date))

            paginator = Paginator(invoices_array, 10)
            page = request.GET.get('page', 1)

            try:
                invoices_array = paginator.page(page)
            except PageNotAnInteger:
                invoices_array = paginator.page(1)
            except EmptyPage:
                invoices_array = paginator.page(paginator.num_pages)

            has_next = invoices_array.has_next()
            has_previous = invoices_array.has_previous()
            has_other_pages = invoices_array.has_other_pages()

            if data['showing_amount']:
                # showing_amount = int(data['showing_amount']) if not data['showing_amount'] == 'All' else len(invoices_array)
                showing_amount = 100
                invoices_array = invoices_array[:showing_amount] if showing_amount >= 10 else invoices_array

            response = {
                'invoices': [invoices_array],
                'invoices_dates': invoices_dates,
                'invoices_number': str(len(all_user_invoices)),
                'showing_amount': str(len(all_user_invoices)),
                'has_next': has_next,
                'has_previous': has_previous,
                'has_other_pages': has_other_pages,
            }

            return JsonResponse(response)

@login_required(login_url='/accounts/login/')
def invoice_detail(request, id):
    invoice = Invoice.objects.get(id=id)
    if request.user.is_superuser or invoice.responsible == request.b24_contact_id:
       
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

    if request.user.is_superuser or invoice.responsible == request.user.b24_contact_id:

        context = {'invoice': invoice}

        template = get_template('invoices/pdf_template.html')
        html = template.render(context)

        pdf_file = BytesIO()
        pisa.CreatePDF(BytesIO(html.encode('utf-8')), pdf_file)

        filename = f'invoice_{id}.pdf'

        response = HttpResponse(pdf_file.getvalue(), content_type='application/pdf')
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % filename

        return response

    else:
        return redirect('/invoices/')
