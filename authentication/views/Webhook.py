from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from authentication.models import WebhookTask, Task, Invoice
from django.conf import settings
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
        entities_id = request.POST.get('data[FIELDS_AFTER][ID]')
        b24_domain = request.POST.get('auth[domain]')
        b24_member_id = request.POST.get('auth[member_id]')
        b24_application_token = request.POST.get('auth[application_token]')
        b24_time = request.POST.get('ts')
        # перевіряємо наявність запису із отриманими данними в таблиці
        # якщо запис є - оновлюємо цю запис
        try:
            webhook_task = WebhookTask.objects.get(entities_id=entities_id, b24_domain=b24_domain)
            webhook_task.entities_id = entities_id
            webhook_task.b24_domain = b24_domain
            webhook_task.b24_member_id = b24_member_id
            webhook_task.b24_application_token = b24_application_token
            webhook_task.b24_time = b24_time
            webhook_task.save()
        # якщо запису немає - записуємо
        except WebhookTask.DoesNotExist:
            WebhookTask.objects.create(
                entities_id=entities_id,
                b24_domain=b24_domain,
                b24_member_id=b24_member_id,
                b24_application_token=b24_application_token,
                b24_time=b24_time
            )
        # тепер з допомогою рест апі бітікса, дістаємо дані про сутність яке зловив вебхук

        task = "tasks.task.get/?id=" + entities_id
        task_url = settings.B24_WEBHOOK + task
        task_load = requests.get(task_url).json()['result']['task']
        # отримуємо дані про користувача який є відповідальним в задачі
        responsible = "user.get/?id=" + task_load['responsible']['id']
        responsible_url = settings.B24_WEBHOOK + responsible
        responsible = requests.get(responsible_url).json()['result']
        # перевіряємо наявність запису данних про задачу в таблиці task
        # якщо запис є - робимо апдейт запису в базі
        try:
            task = Task.objects.get(manager=responsible[0]['EMAIL'], task_id=entities_id)
            task.task_id = entities_id
            task.task = task_load
            task.is_opened = False
            task.save()
        # якщо запису немає - записуємо
        except Task.DoesNotExist:
            Task.objects.create(
                manager=responsible[0]['EMAIL'],
                task_id=entities_id,
                task=task_load,
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
        # перевіряємо наявність запису із отриманими данними в таблиці
        defaults = {
            'b24_member_id': b24_member_id,
            'b24_application_token': b24_application_token,
            'b24_time': b24_time,
        }
        # Оновлюємо значення у випадку, якщо запис уже існує у таблиці.
        # Першим параметром є критерій вибірки об'єктів, які будуть оновлюватися.
        # Другий параметр представляє об'єкт із значеннями, які отримають вибрані об'єкти.
        # Якщо критерію не відповідає жодних об'єктів, то до таблиці додається новий об'єкт.
        # A змінна created дорівнюватиме True.
        webhook_invoice, created = WebhookInvoice.objects.update_or_create(
            entities_id=entities_id,
            b24_domain=b24_domain,
            defaults=defaults,
        )
        # Якщо зміна created дорівнюватиме False то це означає, що метод не створив новий запис,
        # а знайшов відповідний запис в таблиці, використовуючи передані значення полів.
        # У цьому випадку, потрібно оновити значення полів в цьому записі, оскільки вони можуть бути застарілими.
        if not created:
            for key, value in defaults.items():
                setattr(webhook_invoice, key, value)
            webhook_invoice.save()

        # тепер з допомогою рест апі бітікса, дістаємо дані про сутність яке зловив вебхук
        method = "crm.invoice.get/?id=" + entities_id
        url = settings.B24_WEBHOOK + method
        invoice_load = requests.get(url).json()['result']
        # перевіряємо наявність запису данних про інвойса в таблиці invoice
        try:
            invoice_get = Invoice.objects.get(manager=invoice_load['RESPONSIBLE_EMAIL'], invoice_id=invoice_load['ID'])
            invoice_get.manager = invoice_load['RESPONSIBLE_EMAIL']
            invoice_get.invoice_id = invoice_load['ID']
            invoice_get.invoice = invoice_load
            invoice_get.is_opened = False
            invoice_get.save()
        except Invoice.DoesNotExist:
            Invoice.objects.create(
                manager=invoice_load['RESPONSIBLE_EMAIL'],
                invoice_id=invoice_load['ID'],
                invoice=invoice_load,
                is_opened=False
            )
        return HttpResponse()