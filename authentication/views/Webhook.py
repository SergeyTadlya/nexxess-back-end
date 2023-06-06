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
from nexxes_proj import settings
from bs4 import BeautifulSoup
import os
import time
import re


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

            print(all([entities_id, b24_time, b24_domain, b24_member_id, b24_application_token]))

            if all([entities_id, b24_time, b24_domain, b24_member_id, b24_application_token]):

                task_url = set_webhook() + 'tasks.task.get/?id=' + entities_id
                task_crm = set_webhook() + 'tasks.task.get/?taskId=' + entities_id + '&select%5B0%5D=UF_CRM_TASK'
                task_info = requests.get(task_url).json()['result']['task']
                task_info_crm = requests.get(task_crm).json()['result']['task']
                print(f'taskinfo >>>>>>>>>>{task_info}')
                print(f'taskinfocrm>>>>>>{task_info_crm}')

                ticket_title = task_info["title"]
                ticket_text = task_info["description"]
                status = TicketStatus.objects.filter(value=task_info["status"])
                if status.exists():
                    status = status.first()

                deadline = datetime.strptime(task_info["deadline"][:11] + '23:59:59', '%Y-%m-%dT%H:%M:%S')
                created_at = datetime.strptime(task_info["changedDate"][:19], '%Y-%m-%dT%H:%M:%S')
                print(f'>>>>>>>>>>>>>>>>>>{created_at}')

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
                Ticket.objects.update_or_create(task_id=entities_id, defaults=defaults)
                # ticket, created = Ticket.objects.update_or_create(task_id=entities_id, defaults=defaults)
                # if event == "ONTASKADD":
                #     TicketComments.objects.create(
                #         ticket=ticket,
                #         comment_id=0,
                #         text="Wait for manager answer",
                #         manager_name=trim_before(task_info_crm["ufCrmTask"][0]),
                #         is_opened=True,
                #         added_documents=None,
                #         is_active=True,
                #         created_date=datetime.now(),
                #     )
        return HttpResponse('ok')

    except Exception as e:
        print(e)
    return HttpResponse('ok')


@csrf_exempt
def webhook_task_comment(request):
    time.sleep(3)
    try:
        if request.method == 'POST':
            b24keys = B24keys.objects.first()
            event = request.POST.get('event', "")
            entities_id = request.POST.get('data[FIELDS_AFTER][TASK_ID]', "")
            print(f'entititi {entities_id}')
            comment_id = request.POST.get('data[FIELDS_AFTER][ID]', "")
            print('comment_id', comment_id)
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
                comment_isset = True
            # comment is deleted in ticket
            except:
                comment_isset = False

            if comment_isset == True:
                message_text = comment['POST_MESSAGE']
                if comment['AUTHOR_ID'] != '393': # 393
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
                obj, created = TicketComments.objects.get_or_create(
                    ticket=ticket,
                    comment_id=comment_id,
                    defaults={
                        "text": message_text,
                        "manager_name": manager_name,
                        "is_opened": is_opened,             # ticket.is_opened
                        "added_document_type": None,
                        "added_documents_url": None,
                        "added_document_name": None,
                        "is_active": True,
                        "created_date": datetime.now(),
                    },
                )
                # TicketComments.objects.create(
                #     ticket=ticket,
                #     comment_id=comment_id,
                #     text=message_text,
                #     manager_name=manager_name,
                #     is_opened=is_opened,             # ticket.is_opened
                #     added_documents_type=None,  # You can add the documents here
                #     is_active=True,
                #     created_date=datetime.now(),
                # )
            elif event == "ONTASKCOMMENTUPDATE":
                TicketComments.objects.filter(
                    ticket=ticket,
                    comment_id=comment_id,
                ).update(
                    text=message_text,
                    manager_name=manager_name,
                    is_opened=ticket.is_opened,
                    is_active=True,
                )
            else:
                deleted_ticket = TicketComments.objects.filter(
                    ticket=ticket,
                    comment_id=comment_id,
                )
                # delete file from db item
                # file_path = os.path.join(settings.MEDIA_ROOT, deleted_ticket.first().added_documents.path)
                # os.remove(file_path)
                deleted_ticket.delete()

            # if file is isset in comment
            if 'ATTACHED_OBJECTS' in comment:
                for file_data in comment['ATTACHED_OBJECTS']:
                    file_item = file_data
                file_name = comment['ATTACHED_OBJECTS'][file_item]['NAME']
                # get file publick link from bitrix
                file_id = comment['ATTACHED_OBJECTS'][file_item]['FILE_ID']
                file_public_link = bx24.callMethod(
                    "disk.file.getExternalLink",
                    id=int(file_id),
                )
                b24_response = requests.get(file_public_link)
                b24_file_content = b24_response.content
                # parsing file content
                soup = BeautifulSoup(b24_file_content, 'html.parser')
                meta_element = soup.find('meta', property='og:image')
                # its document
                if meta_element is None:
                    # find public url in file type document 
                    pattern = r'href="(/docs/pub/[^"]+)"'
                    matches = re.findall(pattern, b24_file_content.decode())
                    doc_url = matches[0]
                    file_view_url = f'https://{b24_domain}{doc_url}'
                    file_type = "document"
                # its image
                else:
                    file_view_url = meta_element['content']
                    # response = requests.get(file_view_url)
                    # image_content = response.content
                    # content_file = ContentFile(image_content, name=file_name)
                    file_type = "image"                
                
                
                print('file_view_url', file_view_url)
                new_comment = TicketComments.objects.get(ticket=ticket, comment_id=comment_id)
                # new_comment.added_documents.save(file_name, image_file)
                # new_comment.save()
                if new_comment.manager_name != "client":
                    new_comment.added_document_type = file_type
                    new_comment.added_documents_url = file_view_url
                    new_comment.added_document_name = file_name
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
