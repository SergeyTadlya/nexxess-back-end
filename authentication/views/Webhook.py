from authentication.helpers.B24Webhook import set_webhook
from django.views.decorators.csrf import csrf_exempt
from authentication.models import B24keys
from invoices.models import Invoice, Status
from tickets.models import Ticket, Ticket_comments
from django.http import HttpResponse

from invoices.models import Invoice, Status
from tickets.models import Ticket
from datetime import datetime

from bitrix24 import *
import requests
import requests
import logging



def trim_before(text):
    return text.split('_', 1)[1]

def format_date(date):
    return date.strftime('%d %b %Y') if date else ''

@csrf_exempt
def webhook_task(request):
    try:
        if request.method == 'POST':
            # Do system check is webhook received data from task
            event = request.POST.get('event', "")

            if event == "ONTASKADD":
                entities_id = request.POST.get('data[FIELDS_AFTER][ID]', "")
                print(f'task id{entities_id}')
            elif event == "ONTASKUPDATE":
                entities_id = request.POST.get('data[FIELDS_BEFORE][ID]', "")
                print(f'task id{entities_id}')

            # event = request.POST.get('event', "")
            # entities_id = request.POST.get('data[FIELDS_AFTER][TASK_ID]', "")
            b24_domain = request.POST.get('auth[domain]', "")
            print(b24_domain)
            b24_member_id = request.POST.get('auth[member_id]', "")
            print(b24_member_id)
            b24_application_token = request.POST.get('auth[application_token]', "")
            print(b24_application_token)
            b24_time = request.POST.get('ts', "")
            print(b24_time)
            # With help rest api
            print(all([entities_id, b24_domain, b24_member_id, b24_application_token, b24_time]))
            print(([entities_id, b24_domain, b24_member_id, b24_application_token, b24_time]))

            if all([entities_id, b24_domain, b24_member_id, b24_application_token, b24_time]):

                task_url = f"{set_webhook()}tasks.task.get/?id={entities_id}"
                task_crm = f"{set_webhook()}tasks.task.get/?taskId={entities_id}&select%5B0%5D=UF_CRM_TASK"
                print(f'Contact id{task_crm}')
                task_info = requests.get(task_url).json()['result']['task']
                ticket_text = task_info["description"]
                print(ticket_text)
                print(task_info)
                deadline = task_info["deadline"]
                print(f'DEADLINE!! {deadline}')
                status = task_info["status"]
                print(f'status {status}')

                ticket_title = task_info["title"]
                print(f'title {ticket_title}')
                task_info_crm = requests.get(task_crm).json()['result']['task']
                print(task_info_crm)
                created_at = task_info["createdDate"]


                # Check avaible about task
                # if task is avaible do this
                defaults = {
                    'b24_domain': b24_domain,
                    'ticket_title': ticket_title,
                    'b24_member_id': b24_member_id,
                    'b24_application_token': b24_application_token,
                    'b24_time': b24_time,
                    'ticket_text': ticket_text,
                    'task_info': task_info,
                    'deadline': created_at,
                    'status': status,
                    'task_info_crm': task_info_crm,
                    'is_opened': False,
                    'responsible': trim_before(task_info_crm["ufCrmTask"][0]),
                    'created_at': created_at,
                    'is_active': True,
                }
                try:
                    Ticket.objects.update_or_create(
                        task_id=entities_id,
                        defaults=defaults,

                    )
                    print('Success')
                except Exception as e:
                    print(f'Task created error {e}')

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
                    comment = Ticket_comments.objects.create(
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
            if status.exists():
                status = status.first()
            # Check avaible to write in database

            defaults = {
                'b24_domain': b24_domain,
                'b24_member_id': b24_member_id,
                'b24_application_token': b24_application_token,
                'b24_time': b24_time,
                'invoice_info': invoice_load,
                'price': invoice_load['PRICE'],
                'status': status,
                'date': datetime.strptime(invoice_load['DATE_BILL'], '%Y-%m-%dT%H:%M:%S%z'),
                'due_date': datetime.strptime(invoice_load['DATE_PAY_BEFORE'][:11] + '23:59:59', '%Y-%m-%dT%H:%M:%S'),
                'is_opened': False,
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
