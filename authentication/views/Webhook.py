from authentication.helpers.B24Webhook import set_webhook
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from authentication.models import B24keys
from services.models import ServiceCategory
from invoices.models import Invoice, Status
from tickets.models import Ticket, TicketComments, TicketStatus

from datetime import datetime, timedelta
from bitrix24 import *

import requests
from services.models import ServiceCategory, Service
from django.core.files.base import ContentFile


def trim_before(text):
    return text.split('_', 1)[1]


def format_date(date):
    return date.strftime('%d %b %Y') if date else ''


@csrf_exempt
def webhook_task(request):
    # try:
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

        print(all([entities_id, b24_time, b24_domain, b24_member_id, b24_application_token]))

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
                'deadline': deadline,
                'b24_domain': b24_domain,
                'b24_member_id': b24_member_id,
                'b24_application_token': b24_application_token,
                'b24_time': b24_time,
                'task_info': task_info,
                'task_info_crm': task_info_crm,
                'created_at': created_at,
            }

            ticket, created = Ticket.objects.update_or_create(task_id=entities_id, defaults=defaults)
            if event == "ONTASKADD":
                TicketComments.objects.create(
                    ticket=ticket,
                    comment_id=0,
                    text="Wait for manager answer",
                    manager_name=trim_before(task_info_crm["ufCrmTask"][0]),
                    is_opened=True,
                    added_documents=None,
                    is_active=True,
                    created_date=datetime.now(),
                )
    return HttpResponse('ok')

    # except Exception as e:
    #     print(e)
    # return HttpResponse('ok')


@csrf_exempt
def webhook_task_comment(request):
    try:
        if request.method == 'POST':
            b24keys = B24keys.objects.first()
            event = request.POST.get('event', "")
            entities_id = request.POST.get('data[FIELDS_AFTER][TASK_ID]', "")
            comment_id = request.POST.get('data[FIELDS_AFTER][ID]', "")

            domain = b24keys.domain
            rest_key = b24keys.rest_key
            b24_comment = 'task.commentitem.get'
            bx24 = Bitrix24(domain + rest_key)

            # check if comment is isset in ticket
            try:
                comment = bx24.callMethod(
                    b24_comment,
                    taskId=int(entities_id),
                    itemId=int(comment_id),
                )
                print('comment 104', comment)
                comment_isset = True
            # comment is deleted in ticket
            except:
                comment_isset = False

            if comment_isset == True:
                message_text = comment['POST_MESSAGE']
                if comment['AUTHOR_ID'] != '393': #2
                    # get user email
                    userId = comment['AUTHOR_ID']
                    b24User = 'user.get'
                    user = bx24.callMethod(
                        b24User,
                        FILTER={'ID': userId},
                    )
                    manager_name = user[0]['EMAIL']
                    is_opened = False
                else:
                    manager_name = "client"
                    is_opened = True

            ticket = Ticket.objects.get(task_id=entities_id)

            # Get Bitrix24 webhook information
            b24_domain = request.POST.get('auth[domain]', "")
            b24_member_id = request.POST.get('auth[member_id]', "")
            b24_application_token = request.POST.get('auth[application_token]', "")
            b24_time = request.POST.get('ts', "")
            if event == "ONTASKCOMMENTADD":
                TicketComments.objects.create(
                    ticket=ticket,
                    comment_id=comment_id,
                    text=message_text,
                    manager_name=manager_name,
                    is_opened=is_opened,             # ticket.is_opened
                    added_documents=None,  # You can add the documents here
                    is_active=True,
                    created_date=datetime.now(),
                )
            elif event == "ONTASKCOMMENTUPDATE":
                TicketComments.objects.filter(
                    ticket=ticket,
                    comment_id=comment_id,
                ).update(
                    text=message_text,
                    manager_name=manager_name,
                    is_opened=ticket.is_opened,
                    added_documents=None,  # you can add the documents here
                    is_active=True,
                )
            else:
                TicketComments.objects.filter(
                    ticket=ticket,
                    comment_id=comment_id,
                ).delete()

            # if file is isset in comment
            if 'ATTACHED_OBJECTS' in comment:
                for file_data in comment['ATTACHED_OBJECTS']:
                    file_item = file_data

                file_view_url = domain[:-1] + comment['ATTACHED_OBJECTS'][file_item]['VIEW_URL']
                file_name = comment['ATTACHED_OBJECTS'][file_item]['NAME']

                response = requests.get(file_view_url)
                image_content = response.content
                image_file = ContentFile(image_content)

                new_comment = TicketComments.objects.get(ticket=ticket, comment_id=comment_id)
                new_comment.added_documents.save(file_name, image_file)
                new_comment.save()
        return HttpResponse('ok')
    except Exception as e:
        print(e)
        return HttpResponse('error')


@csrf_exempt
def webhook_invoice(request):
    if request.method == 'POST':

        entities_id = request.POST.get('data[FIELDS][ID]', "")
        b24_time = request.POST.get('ts', "")
        b24_domain = request.POST.get('auth[domain]', "")
        b24_member_id = request.POST.get('auth[member_id]', "")
        b24_application_token = request.POST.get('auth[application_token]', "")

        # Check if webhook received data from invoice
        if all([entities_id, b24_time, b24_domain, b24_member_id, b24_application_token]):
            # Now we can get info about invoice
            method = "crm.invoice.get/?id=" + entities_id
            url = set_webhook(method)

            invoice_load = requests.get(url).json()['result']
            status = Status.objects.filter(abbreviation=invoice_load['STATUS_ID'])
            if status.exists():
                status = status.first()

            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            future_time = datetime.now() + timedelta(days=1)

            # Check avaible to write in database
            try:
                date_bill = datetime.strptime(invoice_load['DATE_BILL'] + datetime.now(), '%Y-%m-%dT%H:%M:%S%z')
                # due_time = datetime.strptime(invoice_load['DATE_PAY_BEFORE'][:11] + '23:59:59', '%Y-%m-%dT%H:%M:%S')
                due_time = datetime.strptime(invoice_load['DATE_PAY_BEFORE'][:11] + future_time, '%Y-%m-%dT%H:%M:%S')
            except:
                date_bill = current_time
                due_time = future_time

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
            # first delete all services from deleted category
            Service.objects.filter(category=ServiceCategory.objects.get(category_b24_id=entities_id)).delete()
            # delete category
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
