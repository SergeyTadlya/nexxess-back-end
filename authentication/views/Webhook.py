from authentication.helpers.B24Webhook import set_webhook
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from invoices.models import Invoice, Status
from tickets.models import Ticket
from datetime import datetime

import requests
import logging


@csrf_exempt
def webhook_task(request):
    # Output information about new invoice or new task, which received webhook from bitrix
    if request.method == 'POST':

        # Do system check is webhook received data from task
        event = request.POST.get('event', "")
        if (event == "ONTASKUPDATE"):
            entities_id = request.POST.get('data[FIELDS_AFTER][ID]', "")

            # print(entities_id)
        else:
            entities_id = request.POST.get('data[FIELDS_AFTER][TASK_ID]', "")
            # print(entities_id)

        # event = request.POST.get('event', "")
        # entities_id = request.POST.get('data[FIELDS_AFTER][TASK_ID]', "")
        b24_domain = request.POST.get('auth[domain]', "")
        # print(b24_domain)
        b24_member_id = request.POST.get('auth[member_id]', "")
        b24_application_token = request.POST.get('auth[application_token]', "")
        b24_time = request.POST.get('ts', "")
        # With help rest api
        if entities_id and b24_domain and b24_member_id and b24_application_token and b24_time:
            # task = "tasks.task.get/?id=" + entities_id
            # task_url = B24_WEBHOOK + task
            task_url = f"{set_webhook()}tasks.task.get/?id={entities_id}"
            task_info = requests.get(task_url).json()['result']['task']
            # print(task_info)

            # Give the responsible info
            # responsible = "user.get/?id=" + task_load['responsible']['id']
            # responsible_url = B24_WEBHOOK + responsible

            responsible_url = f"{set_webhook()}user.get/?id={task_info['responsible']['id']}"
            responsible_info = requests.get(responsible_url).json()['result']
            # print(responsible_url)
            # print(responsible_info)

            # Check avaible about task
            # if task is avaible do this
            defaults = {
                'b24_domain': b24_domain,
                'b24_member_id': b24_member_id,
                'b24_application_token': b24_application_token,
                'b24_time': b24_time,
                'task_info': task_info,
                'is_opened': False,
                'responsible': responsible_info['UF_CONTACT_ID']
            }

            try:
                Ticket.objects.update_or_create(
                    task_id=entities_id,
                    defaults=defaults,
                )
            except Exception as e:
                print(e)
        return HttpResponse()


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
                'is_opened': False
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

