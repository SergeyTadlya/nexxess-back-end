from authentication.helpers.B24Webhook import set_webhook
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from bitrix24 import *

from authentication.models import B24keys
from services.models import ServiceCategory
from invoices.models import Invoice, Status
from tickets.models import Ticket, TicketComments, TicketStatus
from datetime import datetime

import requests


def trim_before(text):
    return text.split('_', 1)[1]


def format_date(date):
    return date.strftime('%d %b %Y') if date else ''


@csrf_exempt
def webhook_task(request):
    try:
        if request.method == 'POST':
            event = request.POST.get('event', "")

            if event == "ONTASKADD":
                entities_id = request.POST.get('data[FIELDS_AFTER][ID]', "")
            elif event == "ONTASKUPDATE":
                entities_id = request.POST.get('data[FIELDS_BEFORE][ID]', "")

            b24_time = request.POST.get('ts', "")
            b24_domain = request.POST.get('auth[domain]', "")
            b24_member_id = request.POST.get('auth[member_id]', "")
            b24_application_token = request.POST.get('auth[application_token]', "")

            if all([entities_id, b24_time, b24_domain, b24_member_id, b24_application_token]):

                task_url = set_webhook() + 'tasks.task.get/?id=' + entities_id
                task_crm = set_webhook() + 'tasks.task.get/?taskId=' + entities_id + '&select%5B0%5D=UF_CRM_TASK'
                task_info = requests.get(task_url).json()['result']['task']
                task_info_crm = requests.get(task_crm).json()['result']['task']

                ticket_title = task_info["title"]
                ticket_text = task_info["description"]
                status = TicketStatus.objects.filter(value=task_info["status"])
                if status.exists():
                    status = status.first()
                deadline = datetime.strptime(task_info["deadline"][:11] + '23:59:59', '%Y-%m-%dT%H:%M:%S')
                created_at = task_info["createdDate"]

                defaults = {
                    'responsible': trim_before(task_info_crm["ufCrmTask"][0]),
                    'ticket_title': ticket_title,
                    'ticket_text': ticket_text,
                    'status': status,
                    'is_opened': False,
                    'is_active': True,
                    'deadline': deadline ,
                    'b24_domain': b24_domain,
                    'b24_member_id': b24_member_id,
                    'b24_application_token': b24_application_token,
                    'b24_time': b24_time,
                    'task_info': task_info,
                    'task_info_crm': task_info_crm,
                    'created_at': created_at,

                }

                Ticket.objects.update_or_create(task_id=entities_id, defaults=defaults)
        return HttpResponse('ok')

    except Exception as e:
        print(e)
    return HttpResponse('ok')


@csrf_exempt
def webhook_task_comment(request):
    try:
        if request.method == 'POST':
            b24keys = B24keys.objects.first()

            event = request.POST.get('event', "")

            if event == "ONTASKCOMMENTADD":
                entities_id = request.POST.get('data[FIELDS_AFTER][TASK_ID]', "")
                print(entities_id)
                comment_id = request.POST.get('data[FIELDS_AFTER][ID]', "")
                print(comment_id)
                ######
                # print(set_webhook.domain)
                # print(set_webhook.rest_key)
                domain = b24keys.domain
                print(f'domain{domain}')
                rest_key = b24keys.rest_key
                print(f'rest_key{rest_key}')
                method = 'task.commentitem.getlist'

                b24Comments = 'task.commentitem.getlist'
                bx24 = Bitrix24(domain + rest_key)

                comments = bx24.callMethod(
                    b24Comments,
                    taskId=int(entities_id),
                )
                print(comments)
                # get user email
                userId = comments[0]['AUTHOR_ID']
                b24User = 'user.get'
                user = bx24.callMethod(
                    b24User,
                    FILTER={'ID': userId},
                )
                print(user[0]['EMAIL'])
                manager_name = user[0]['EMAIL']
                print(f'manager name {manager_name}')
                message_text = comments[-1]['POST_MESSAGE']
                print(f'message text {message_text}')
                #######
                ticket = Ticket.objects.get(task_id=entities_id)
                print(ticket)



                # Get Bitrix24 webhook information
                b24_domain = request.POST.get('auth[domain]', "")
                b24_member_id = request.POST.get('auth[member_id]', "")
                b24_application_token = request.POST.get('auth[application_token]', "")
                b24_time = request.POST.get('ts', "")

                if all([comment_id, ticket, b24_domain, b24_member_id, b24_application_token, b24_time]):
                    comment = TicketComments.objects.create(
                        ticket=ticket,
                        comment_id=comment_id,
                        text=message_text,
                        manager_name=manager_name,
                        is_opened=ticket.is_opened,
                        added_documents=None,  # you can add the documents here
                        is_active=True,
                    )
                    print(f"New comment added to ticket {ticket.task_id} with comment id {comment.comment_id}")
        return HttpResponse('ok')
    except Exception as e:
        print(e)
        return HttpResponse('error')


@csrf_exempt
def webhook_invoice(request):
    if request.method == 'POST':
        # check if webhook received data from invoice
        entities_id = request.POST.get('data[FIELDS][ID]', "")
        b24_domain = request.POST.get('auth[domain]', "")
        b24_member_id = request.POST.get('auth[member_id]', "")
        b24_application_token = request.POST.get('auth[application_token]', "")
        b24_time = request.POST.get('ts', "")

        # Now we can get info about invoice
        if entities_id != "" and b24_domain != "" \
                and b24_member_id != "" and b24_application_token != "" \
                and b24_time != "":
            method = "crm.invoice.get/?id=" + entities_id
            url = set_webhook(method)

            invoice_load = requests.get(url).json()['result']
            status = Status.objects.filter(abbreviation=invoice_load['STATUS_ID'])
            print('status>>>>>', status)
            # status = invoice_load['STATUS_ID']
            print('type', type(status))
            print('status len>>>>>', len(status))
            if status.exists():
                status = status.first()
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # Check avaible to write in database
            try:
                date_bill = datetime.strptime(invoice_load['DATE_BILL'], '%Y-%m-%dT%H:%M:%S%z')
                due_time = datetime.strptime(invoice_load['DATE_PAY_BEFORE'][:11] + '23:59:59', '%Y-%m-%dT%H:%M:%S')
            except:
                date_bill = current_time
                due_time = current_time

            defaults = {
                'b24_domain': b24_domain,
                'b24_member_id': b24_member_id,
                'b24_application_token': b24_application_token,
                'b24_time': b24_time,
                'service_id': invoice_load['PRODUCT_ROWS'][0]['PRODUCT_ID'],
                'invoice_info': invoice_load,
                'price': invoice_load['PRICE'],
                'status': status,
                'date': date_bill,
                'due_date': due_time,
                'product_title': ', '.join([row['PRODUCT_NAME'] for row in invoice_load['PRODUCT_ROWS']])
            }


            try:
                Invoice.objects.update_or_create(
                    responsible=invoice_load['UF_CONTACT_ID'],
                    invoice_id=invoice_load['ID'],
                    defaults=defaults,
                )
            except Exception as e:
                print(e)
            return HttpResponse()



@csrf_exempt
def webhook_service_section(request):
    if request.method == 'POST':
        event = request.POST.get('event', "")
        entities_id = request.POST.get('data[FIELDS][ID]', "")
        if event == "ONCRMPRODUCTSECTIONDELETE":
            ServiceCategory.objects.filter(category_b24_id=entities_id).delete()
        else:
            url = set_webhook()
            bx24 = Bitrix24(url)
            section = bx24.callMethod('crm.productsection.get', id=entities_id)

            obj, created = ServiceCategory.objects.update_or_create(
                category_b24_id=section["ID"],
                defaults={'category_name':section["NAME"]}
            )

        return HttpResponse('ok')
