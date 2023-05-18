from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import get_template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest

from authentication.helpers.B24Webhook import set_webhook
from services.models import Service
from tickets.models import Ticket, TicketStatus

from .models import Invoice, Status, StripeSettings, LocalInvoice

from bitrix24 import Bitrix24, BitrixError
from datetime import datetime

import stripe
import json
import time
import fitz


def format_date(date):
    return date.strftime('%d %b %Y') if date else ''


def format_price(price):
    price = str(price)
    price = price.rstrip('0').rstrip('.') if '.' in price else price

    return f'${price}' if price else ''


@login_required(login_url='/accounts/login/')
def invoices(request):
    if request.user.is_authenticated and request.user.google_auth or request.user.is_superuser:
        all_user_invoices = Invoice.objects.all().order_by('-date') if request.user.is_superuser \
            else Invoice.objects.filter(responsible=request.user.b24_contact_id).order_by('-date')

        all_statuses = Status.objects.all()
        statuses = (status.value for status in all_statuses)
        statuses_quantity = (value - value for value in range(len(all_statuses)))
        invoices_array = list()
        invoices_dates = list()
        statuses_number = {key: value for key, value in zip(statuses, statuses_quantity)}
        invoices_statuses = list()

        for invoice in all_user_invoices:

            statuses_number[invoice.status.value] = 1 if invoice.status.value not in statuses_number.keys() \
                else statuses_number[invoice.status.value] + 1

            invoices_array.append({
                'id': invoice.id,
                'invoice_id': invoice.invoice_id,
                'responsible': invoice.responsible,
                'price': format_price(invoice.price),
                'date': format_date(invoice.date),
                'due_date': format_date(invoice.due_date),
                'status': invoice.status,
                'title': invoice.product_title,
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
    else: return redirect('authentication:main')


def ajax_invoice_filter(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        if request.method == 'POST':
            data = json.load(request)
            statuses = [keys for keys in data if data[keys] is True]

            all_user_invoices = Invoice.objects.all().order_by('-date') if request.user.is_superuser else Invoice.objects.filter(responsible=request.user.b24_contact_id).order_by('-date')
            invoices_array = list()
            invoices_dates = list()

            if 'ascending' in data.keys():
                all_user_invoices = all_user_invoices.order_by(data['ascending'])
            elif 'descending' in data.keys():
                all_user_invoices = all_user_invoices.order_by('-' + data['descending'])

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
            page_range = list(invoices_array.paginator.page_range)
            next_page = invoices_array.number + 1 if invoices_array.has_next() else invoices_array.number
            previous_page = invoices_array.number - 1 if invoices_array.has_previous() else invoices_array.number

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
                'page_range': page_range,
                'next_page': next_page,
                'previous_page': previous_page
            }

            return JsonResponse(response)


@login_required(login_url='/accounts/login/')
def invoice_detail(request, id):
    if request.user.is_authenticated and request.user.google_auth or request.user.is_superuser:
        try:
            invoice = Invoice.objects.get(id=id)
            if request.user.is_superuser or int(invoice.responsible) == request.user.b24_contact_id:
                if not request.user.is_superuser and invoice.status.value != 'Paid':
                    Invoice.objects.filter(id=id).update(status=Status.objects.get(value='Opened'))
                invoice = Invoice.objects.get(id=id)
                status_closed = Ticket.objects.filter(responsible=str(request.user.b24_contact_id),  status__name='Closed').count()
                status_overdue = Ticket.objects.filter(responsible=str(request.user.b24_contact_id),  status__name='Overdue').count()
                status_ongoin = Ticket.objects.filter(responsible=str(request.user.b24_contact_id),  status__name='Ongoing').count()

                # product description
                url = set_webhook()
                bx24 = Bitrix24(url)
                product = bx24.callMethod('crm.product.get', id=invoice.service_id)
                description_parts = product['DESCRIPTION'].split("<br>")
                res = {
                    'invoice': invoice,
                    'status_closed': status_closed,
                    'status_overdue': status_overdue,
                    'status_ongoin': status_ongoin,
                    'description_parts': description_parts,
                }
                return render(request, "invoices/detail.html", res)
            else:
                return redirect('/invoices/')
        except :
                return redirect('/invoices/')
    else: return redirect('authentication:main')


def generate_new_pdf(pdf_path, id, invoice, request):

    pdf_file = fitz.open(pdf_path)

    # Load the first page of the PDF
    page = pdf_file.load_page(0)

    # Insert the invoice id
    page.insert_text(fitz.Point(115, 206), str(invoice.invoice_id), fontsize = 16)

    # Insert the date
    page.insert_text(fitz.Point(105, 225), str(format_date(invoice.date)))
    data = str(request.user.first_name) + ' ' + str(request.user.last_name)
    page.insert_text(fitz.Point(100, 342), str((invoice.product_title)), fontsize = 12)

    # Insert the due date
    page.insert_text(fitz.Point(95, 241), str(format_date(invoice.due_date)))
    page.insert_text(fitz.Point(105, 283), str(data), fontsize = 14)
    # Insert the price
    page.insert_text(fitz.Point(469, 343), str(format_price(invoice.price)))
    page.insert_text(fitz.Point(469, 400), str(format_price(invoice.price)))
    page.insert_text(fitz.Point(469, 492), str(format_price(invoice.price)))

    # Save the modified PDF with a new name
    new_file_path = f'pdf_client/invoice_{id}.pdf'
    pdf_file.save(new_file_path)

    return new_file_path


@login_required(login_url='/accounts/login/')
def create_invoice_pdf(request, id):
    invoice = Invoice.objects.get(id=id)
    invoice.responsible = int(invoice.responsible)
    # try:
    if invoice.responsible == request.user.b24_contact_id or request.user.is_superuser:
        if invoice.status.value == 'Paid':
            pdf_template_path = 'invoices/PDF_templates/invoice_template.pdf'
        else:
            pdf_template_path = 'invoices/PDF_templates/invoice_ordinary.pdf'

        generated_pdf_path = generate_new_pdf(pdf_template_path, id, invoice, request)
        binary_pdf = open(generated_pdf_path, 'rb')

        response = HttpResponse(binary_pdf, content_type='application/pdf')
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=%s.pdf' % generated_pdf_path

        return response


@login_required(login_url='/accounts/login/')
@csrf_exempt
def create_payment_link(request):
    stipe_settings = StripeSettings.objects.all().first()
    stripe.api_key = stipe_settings.secret_key
    b24_invoice_id = request.POST["b24_invoice_id"]
    invoice = LocalInvoice.objects.get(b24_invoice_id=b24_invoice_id)
    stripe_response = stripe.PaymentLink.create(
        line_items=[
            {
                "price": invoice.stripe_price_id,
                "quantity": 1,
            },
        ],
        metadata={"b24_invoice_id": b24_invoice_id},
        after_completion={"type": "redirect", "redirect": {"url": stipe_settings.webhook_url+b24_invoice_id},}
    )
    print(stripe_response)
    return JsonResponse({'pay_link': stripe_response.url})


@csrf_exempt
def complete_payment_link(request):
    b24invoice_id = request.GET["b24invoice_id"]
    url = set_webhook("")
    bx24 = Bitrix24(url)
    bx24.callMethod('crm.invoice.update', id=b24invoice_id, fields={'STATUS_ID': 'P',})
    time.sleep(5)
    return redirect("/invoices/")
