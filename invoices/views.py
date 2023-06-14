from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest

from authentication.helpers.B24Webhook import set_webhook
from tickets.models import Ticket, TicketStatus
from .helpers import PaymentHelper, RightSignatureHelper, BitrixHelper

from .models import Invoice, Status, StripeSettings, LocalInvoice

from bitrix24 import Bitrix24, BitrixError
from datetime import datetime, timedelta

import requests
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

def create_task(responsible_id, invoice):
    try:
        method = "tasks.task.add"
        url = set_webhook(method)
        current_datetime = (datetime.now() + timedelta(days=365)).strftime("%b.%d.%Y")
        # hours, minutes, seconds = map(int, invoice.time_remaining.split(':'))
        # time_delta = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        time_estimate = invoice.time_remaining
        print(f'>>>>>>>>{invoice.invoice_id}')
        print(f'>>>type{type(invoice.invoice_id)}')
        task_data = {
            'fields': {
                'TITLE': f'Bought Service{invoice.product_title}',
                'DESCRIPTION': invoice.service_id + ' | ' + invoice.product_title,
                'DEADLINE': current_datetime,
                'CREATED_BY': 393,
                'RESPONSIBLE_ID': 312,
                'PRIORITY': 1,
                'ALLOW_CHANGE_DEADLINE': 1,
                'ALLOW_TIME_TRACKING': 1,
                'TIME_ESTIMATE': time_estimate,
                'UF_CRM_TASK': {
                    "0": 'C_' + responsible_id,  # bitrix24_id
                    },
                "UF_OLD_INVOICE": invoice.invoice_id,
            }
        }
        response = requests.post(url, json=task_data)
        if response.status_code == 200:
            print('Successfully created')
        else:
            print('Error:', response.text)
    except Exception as e:
        print('Error:', str(e))

@login_required(login_url='/accounts/login/')
def invoices(request):
    if request.user.is_authenticated and request.user.google_auth or request.user.is_superuser:

        # Get all user invoices and sorting by created date
        all_user_invoices = Invoice.objects.all().order_by('-date') if request.user.is_superuser \
            else Invoice.objects.filter(responsible=request.user.b24_contact_id).order_by('-date')
        paid_invoice_status = Status.objects.get(abbreviation="P", value="Paid")
        paid_invoices = Invoice.objects.filter(responsible=request.user.b24_contact_id, status=paid_invoice_status, task_created=False)
        for invoice in paid_invoices:
            responsible = str(request.user.b24_contact_id)
            if not invoice.task_created:
                create_task(responsible, invoice)
                invoice.task_created = True
                invoice.save()

        # Get all existing statuses for user invoices
        all_statuses = Status.objects.all()
        statuses = (status.value for status in all_statuses)
        statuses_quantity = (value - value for value in range(len(all_statuses)))
        statuses_number = {key: value for key, value in zip(statuses, statuses_quantity)}
        bought_services = Invoice.objects.filter(responsible=str(request.user.b24_contact_id), status__value='Paid')

        # Iterate through the array and put every specified field into a list
        date_count = 0
        invoices_array = list()
        for index, invoice in enumerate(all_user_invoices):

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

            # Condition for removing bugs with pagination
            if not invoices_array[date_count]['date'] == format_date(invoice.date) or index == 0:
                date_count = index
                invoices_array[index]['more_one'] = True
            else:
                invoices_array[index]['more_one'] = False

        # Get all existing statuses and their quantity for user invoices
        invoices_statuses = list()
        for index, (status_name, status_number) in enumerate(statuses_number.items()):
            invoices_statuses.append({
                'id': 'status' + str(index + 1),
                'name': status_name,
                'number': status_number
            })

        # Sorting for invoices on page
        sort_order = 0
        sort_by = 0

        if request.GET.get('invoice_field'):
            sort_order = request.GET.get('state') == 'true'
            sort_by = request.GET.get('invoice_field')
        elif request.session.get('for_sort'):
            sort_order = request.session.get('for_sort')[0]
            sort_by = request.session.get('for_sort')[1]

        try:
            if sort_by == 'invoice_id':
                invoices_array = sorted(invoices_array, key=lambda x: int(x[sort_by]), reverse=sort_order)
            elif sort_by == 'status':
                invoices_array = sorted(invoices_array, key=lambda x: x[sort_by].value, reverse=sort_order)
            elif sort_by == 'price':
                invoices_array = sorted(invoices_array, key=lambda x: int(x[sort_by][1:]), reverse=sort_order)
            else:
                invoices_array = sorted(invoices_array, key=lambda x: x[sort_by], reverse=sort_order)
            request.session['for_sort'] = [sort_order, sort_by]
        except KeyError:
            pass

        # Pagination for invoices
        limit = request.GET.get('limit', '10')
        if not limit.isdigit():
            limit = len(invoices_array)

        paginator = Paginator(invoices_array, limit)
        page = request.GET.get('page', 1)

        try:
            invoices_array = paginator.page(page)
        except PageNotAnInteger:
            invoices_array = paginator.page(1)
        except EmptyPage:
            invoices_array = paginator.page(paginator.num_pages)

        context = {
            "invoices": invoices_array,
            'invoices_statuses': invoices_statuses,
            'statuses_amount': len(invoices_statuses),
            'invoices_number': len(all_user_invoices),
            'bought_services': bought_services,
            'amount_on_page': limit,
        }

        return render(request, "invoices/invoices.html", context)
    else:
        return redirect('authentication:main')


def ajax_invoice_filter(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        if request.method == 'POST':
            data = json.load(request)
            statuses = [keys for keys in data if data[keys] is True]

            # Get all user invoices and sorting by created date
            all_user_invoices = Invoice.objects.all().order_by('-date') if request.user.is_superuser else Invoice.objects.filter(responsible=request.user.b24_contact_id).order_by('-date')

            # Ascending or Descending filtering by the field selected by the user
            if 'ascending' in data.keys():
                all_user_invoices = all_user_invoices.order_by(data['ascending'])
            elif 'descending' in data.keys():
                all_user_invoices = all_user_invoices.order_by('-' + data['descending'])

            # Invoices existing statuses
            if statuses:
                all_user_invoices = all_user_invoices.filter(status__value__in=statuses)

            # Calendar filtering
            if data['from_date'] and data['to_date']:
                all_user_invoices = all_user_invoices.filter(
                    date__gte=datetime.strptime(data['from_date'] + 'T00:00:00', '%B.%d.%YT%H:%M:%S'),
                    date__lte=datetime.strptime(data['to_date'] + 'T23:59:59', '%B.%d.%YT%H:%M:%S')
                )
            elif data['from_date']:
                all_user_invoices = all_user_invoices.filter(
                    date__gte=datetime.strptime(data['from_date'] + 'T00:00:00', '%B.%d.%YT%H:%M:%S'),
                )
            elif data['to_date']:
                all_user_invoices = all_user_invoices.filter(
                    date__lte=datetime.strptime(data['to_date'] + 'T23:59:59', '%B.%d.%YT%H:%M:%S')
                )

            # Local search
            if data['local_search']:
                all_user_invoices = all_user_invoices.filter(
                    Q(invoice_id__icontains=data['local_search']) |
                    Q(price__icontains=data['local_search']) |
                    Q(status__value__icontains=data['local_search']) |
                    Q(date__icontains=data['local_search']) |
                    Q(due_date__icontains=data['local_search'])
                )

            # Iterate through the array and put everything into a list
            date_count = 0
            invoices_array = list()
            for index, invoice in enumerate(all_user_invoices):
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

                # Condition for removing bugs with pagination
                if not invoices_array[date_count]['date'] == format_date(invoice.date) or index == 0:
                    date_count = index
                    invoices_array[index]['more_one'] = True
                else:
                    invoices_array[index]['more_one'] = False

            # Pagination for tickets
            paginator = Paginator(invoices_array, 10)
            page = request.GET.get('page', 1)

            try:
                invoices_array = paginator.page(page)
            except PageNotAnInteger:
                invoices_array = paginator.page(1)
            except EmptyPage:
                invoices_array = paginator.page(paginator.num_pages)

            # Get all pagination data for converting to json format
            has_next = invoices_array.has_next()
            has_previous = invoices_array.has_previous()
            has_other_pages = invoices_array.has_other_pages()
            page_range = list(invoices_array.paginator.page_range)
            next_page = invoices_array.number + 1 if invoices_array.has_next() else invoices_array.number
            previous_page = invoices_array.number - 1 if invoices_array.has_previous() else invoices_array.number

            # Not working yet
            if data['showing_amount']:
                # showing_amount = int(data['showing_amount']) if not data['showing_amount'] == 'All' else len(invoices_array)
                showing_amount = 100
                invoices_array = invoices_array[:showing_amount] if showing_amount >= 10 else invoices_array

            response = {
                'invoices': [invoices_array],
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
                # description_parts = product['DESCRIPTION'].split("<br>")
                parts_array = product['DESCRIPTION'].split("<br>")
                description_parts = [item.replace("&nbsp;", "").strip() for item in parts_array if item.strip()]

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
        except:
            return redirect('/invoices/')
    else:
        return redirect('authentication:main')



def generate_new_pdf(pdf_path, id, invoice, request):
    pdf_file = fitz.open(pdf_path)

    # Load the first page of the PDF
    page = pdf_file.load_page(0)

    # Insert the invoice id
    page.insert_text(fitz.Point(115, 206), str(invoice.invoice_id), fontsize=16)

    # Insert the date
    page.insert_text(fitz.Point(105, 225), str(format_date(invoice.date)))
    data = str(request.user.first_name) + ' ' + str(request.user.last_name)
    page.insert_text(fitz.Point(100, 342), str((invoice.product_title)), fontsize=12)

    # Insert the due date
    page.insert_text(fitz.Point(95, 241), str(format_date(invoice.due_date)))
    page.insert_text(fitz.Point(105, 283), str(data), fontsize=14)
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
    print(f'>>>>>>invoice_id>>>>>>>{b24_invoice_id}')
    print(f'type {type(b24_invoice_id)}')
    invoice = LocalInvoice.objects.get(b24_invoice_id=b24_invoice_id)
    stripe_response = stripe.PaymentLink.create(
        line_items=[
            {
                "price": invoice.stripe_price_id,
                "quantity": 1,
            },
        ],
        metadata={"b24_invoice_id": b24_invoice_id},
        after_completion={"type": "redirect", "redirect": {"url": stipe_settings.webhook_url + b24_invoice_id}, }
    )
    print(stripe_response)
    return {'pay_link': stripe_response.url}


@login_required(login_url='/accounts/login/')
@csrf_exempt
def check_user_sign(request):
    user_id = request.POST.get('user_id')
    b24_invoice_id = request.POST.get('b24_invoice_id')

    sign_helper = RightSignatureHelper()

    contact = BitrixHelper.get_contact(user_id)
    if contact.get('status') == 'error':
        return JsonResponse(data=contact, status=200)

    invoice = BitrixHelper.get_invoice(b24_invoice_id)
    if invoice.get('status') == 'error':
        return JsonResponse(data=invoice, status=200)

    product = BitrixHelper.get_product(invoice['PRODUCT_ROWS'][0]['PRODUCT_ID'])
    if product.get('status') == 'error':
        return JsonResponse(data=invoice, status=200)

    # If 'Pay' button pressed first time - field with Signed File in Invoice is None
    if invoice[BitrixHelper.INVOICE_SIGNED_FILE] is None:
        sign_helper.send_document(contact, invoice, product)

        return JsonResponse(
            data={
                'status': "document_sent",
                'message': f"Please, check your mailbox and sign File and then press 'Pay' button again to get a payment link"
            },
            status=200
        )

    # File were sent but not signed
    is_signed = PaymentHelper.is_file_signed(contact, invoice)
    if not is_signed:
        status = sign_helper.check_status(contact, invoice)

        if not status:
            message = "Please, check your mailbox and sign the file, then press the 'Pay' button again to get a payment link."
        else:
            message = "File signed successfully."
            payment_link = create_payment_link(request)

        return JsonResponse(
            data={
                'status': 'not_signed' if not status else 'link',
                'message': message,
                'link': payment_link['pay_link'] if status else None
            },
            status=200
        )
    else:
        payment_link = create_payment_link(request)

        # If invoice was paid, don't send payment link again
        if invoice['STATUS_ID'] == 'P':
            return JsonResponse(
                data={
                    'status': 'paid',
                    'message': "Your invoice was paid. Please, wait until status change to 'Paid'"
                },
                status=200
            )
        else:
            return JsonResponse(
                data={
                    'status': 'link',
                    'link': payment_link['pay_link']
                },
                status=200
            )


@csrf_exempt
def complete_payment_link(request):
    b24invoice_id = request.GET["b24invoice_id"]
    url = set_webhook("")
    bx24 = Bitrix24(url)
    bx24.callMethod('crm.invoice.update', id=b24invoice_id, fields={'STATUS_ID': 'P', })
    time.sleep(5)
    return redirect("/invoices/")
