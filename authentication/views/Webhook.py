from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from authentication.models import Ticket, Invoice, B24keys
from authentication.helpers.B24Webhook import B24_WEBHOOK
import requests


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
        entities_id = request.POST.get('data[FIELDS_AFTER][ID]', "")
        b24_domain = request.POST.get('auth[domain]', "")
        b24_member_id = request.POST.get('auth[member_id]', "")
        b24_application_token = request.POST.get('auth[application_token]', "")
        b24_time = request.POST.get('ts', "")
        # тепер з допомогою рест апі бітікса, дістаємо дані про сутність яке зловив вебхук
        if entities_id != "" and b24_domain != "" \
                and b24_member_id != "" and b24_application_token != "" \
                and b24_time != "":
            task = "tasks.task.get/?id=" + entities_id
            task_url = B24_WEBHOOK + task
            task_load = requests.get(task_url).json()['result']['task']
            # отримуємо дані про користувача який є відповідальним в задачі
            responsible = "user.get/?id=" + task_load['responsible']['id']
            responsible_url = B24_WEBHOOK + responsible
            responsible = requests.get(responsible_url).json()['result']
            # перевіряємо наявність запису данних про задачу в таблиці task
            # якщо запис є - робимо апдейт запису в базі, якщо немає - створюємо
            defaults = {
                'b24_domain': b24_domain,
                'b24_member_id': b24_member_id,
                'b24_application_token': b24_application_token,
                'b24_time': b24_time,
                'task_info': task_load,
                'is_opened': False
            }

            Ticket.objects.update_or_create(
                responsible=responsible[0]['EMAIL'],
                task_id=entities_id,
                defaults=defaults,
            )
        return HttpResponse()


@csrf_exempt
def webhook_invoice(request):
    if request.method == 'POST':
        # виконуємо перевірку чи вебхук отримав дані із інвойса
        entities_id = request.POST.get('data[FIELDS][ID]', "")
        b24_domain = request.POST.get('auth[domain]', "")
        b24_member_id = request.POST.get('auth[member_id]', "")
        b24_application_token = request.POST.get('auth[application_token]', "")
        b24_time = request.POST.get('ts', "")
        # тепер з допомогою рест апі бітікса, дістаємо дані про сутність яке зловив вебхук
        if entities_id != "" and b24_domain != "" \
                and b24_member_id != "" and b24_application_token != "" \
                and b24_time != "":
            method = "crm.invoice.get/?id=" + entities_id
            url = B24_WEBHOOK + method
            invoice_load = requests.get(url).json()['result']
            # перевіряємо наявність запису данних про інвойса в таблиці invoice
            # якщо запис є - робимо апдейт запису в базі, якщо немає - створюємо
            defaults = {
                'b24_domain': b24_domain,
                'b24_member_id': b24_member_id,
                'b24_application_token': b24_application_token,
                'b24_time': b24_time,
                'invoice_info': invoice_load,
                'price': invoice_load['PRICE'],
                'is_opened': False
            }

            Invoice.objects.update_or_create(
                responsible=invoice_load['RESPONSIBLE_EMAIL'],
                invoice_id=invoice_load['ID'],
                defaults=defaults,
            )
            return HttpResponse()