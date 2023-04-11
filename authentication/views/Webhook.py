from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from authentication.models import Ticket, Invoice, B24keys
from django.conf import settings
import requests

try:
    B24keys = B24keys.objects.get(id=1)     # get b24 keys from db (1 - id)
    B24_WEBHOOK = B24keys.b24_webhook       # init b24 webhook
except B24keys.DoesNotExist:
    B24keys = ""


@csrf_exempt
def webhook_task(request):
    # вебхук бітрікса відправляє дані через post
    if request.method == 'POST':
        # вебхук, по задачам, відправляє нові поля
        # 'data[FIELDS_BEFORE][ID]': ['2'],
        # 'data[FIELDS_AFTER][ID]': ['2'],
        # 'data[IS_ACCESSIBLE_BEFORE]': ['undefined'],
        # 'data[IS_ACCESSIBLE_AFTER]': ['undefined']

        # виконуємо перевірку чи вебхук отримав дані із задачі
        entities_id = request.POST.get('data[FIELDS_AFTER][ID]')
        b24_domain = request.POST.get('auth[domain]')
        b24_member_id = request.POST.get('auth[member_id]')
        b24_application_token = request.POST.get('auth[application_token]')
        b24_time = request.POST.get('ts')
        # тепер з допомогою рест апі бітікса, дістаємо дані про сутність яке зловив вебхук
        task = "tasks.task.get/?id=" + entities_id
        task_url = B24_WEBHOOK + task
        task_load = requests.get(task_url).json()['result']['task']
        # отримуємо дані про користувача який є відповідальним в задачі
        responsible = "user.get/?id=" + task_load['responsible']['id']
        responsible_url = B24_WEBHOOK + responsible
        responsible = requests.get(responsible_url).json()['result']
        # перевіряємо наявність запису данних про задачу в таблиці task
        # якщо запис є - робимо апдейт запису в базі
        try:
            task = Ticket.objects.get(responsible=responsible[0]['EMAIL'], task_id=entities_id)
            task.task_id = entities_id
            task.b24_domain = b24_domain
            task.b24_member_id = b24_member_id
            task.b24_application_token = b24_application_token
            task.b24_time = b24_time
            task.task_info = task_load
            task.is_opened = False
            task.save()
        # якщо запису немає - записуємо
        except Ticket.DoesNotExist:
            Ticket.objects.create(
                responsible=responsible[0]['EMAIL'],
                task_id=entities_id,
                b24_domain=b24_domain,
                b24_member_id=b24_member_id,
                b24_application_token=b24_application_token,
                b24_time=b24_time,
                task_info=task_load,
                is_opened=False
            )
        return HttpResponse()


@csrf_exempt
def webhook_invoice(request):
    if request.method == 'POST':
        # виконуємо перевірку чи вебхук отримав дані із інвойса
        entities_id = request.POST.get('data[FIELDS][ID]')
        b24_domain = request.POST.get('auth[domain]')
        b24_member_id = request.POST.get('auth[member_id]')
        b24_application_token = request.POST.get('auth[application_token]')
        b24_time = request.POST.get('ts')
        # тепер з допомогою рест апі бітікса, дістаємо дані про сутність яке зловив вебхук
        method = "crm.invoice.get/?id=" + entities_id
        url = B24_WEBHOOK + method
        invoice_load = requests.get(url).json()['result']
        print('price', invoice_load['PRICE'])
        # перевіряємо наявність запису данних про інвойса в таблиці invoice
        try:
            invoice_get = Invoice.objects.get(responsible=invoice_load['RESPONSIBLE_EMAIL'], invoice_id=invoice_load['ID'])
            invoice_get.responsible = invoice_load['RESPONSIBLE_EMAIL']
            invoice_get.invoice_id = invoice_load['ID']
            invoice_get.b24_domain = b24_domain
            invoice_get.b24_member_id = b24_member_id
            invoice_get.b24_application_token = b24_application_token
            invoice_get.b24_time = b24_time
            invoice_get.invoice_info = invoice_load
            invoice_get.price = invoice_load['PRICE']
            invoice_get.is_opened = False
            invoice_get.save()
        except Invoice.DoesNotExist:
            Invoice.objects.create(
                responsible=invoice_load['RESPONSIBLE_EMAIL'],
                invoice_id=invoice_load['ID'],
                b24_domain=b24_domain,
                b24_member_id=b24_member_id,
                b24_application_token=b24_application_token,
                b24_time=b24_time,
                invoice_info=invoice_load,
                price=invoice_load['PRICE'],
                is_opened=False
            )
        return HttpResponse()
    #
    # print("invoice_load['ID']")
    # print('PRICE')
    # print("invoice_get.price")
    # print("invoice_load('PRICE')")