from django.shortcuts import render, redirect
from authentication.models import Invoice
import requests
import json


def b24_webhook(request):
    res = request
    return render(request, "main.html", res)


def main(request):
    if not request.user.is_authenticated:
        return redirect("/accounts/login/")
    else:
        # виведення інформації про новий інвойс чи нову задачу, який отримав вебхук бітрікса
        url = "https://apps.devplace.info/client_apps/nexxess/webhook.php"
        get_request = requests.get(url)
        webhook = get_request.text
        info = json.loads(webhook)
        if(info['event'] == 'ONCRMINVOICEADD'): # invoice
            invoice_url = "https://b24-hx1f8l.bitrix24.eu/rest/1/36b359umrza782tx/crm.invoice.get/?id=" + info['data']['FIELDS']['ID']
            invoice_request = requests.get(invoice_url)
            invoice_load = json.loads(invoice_request.text)
            invoice = {
                'id': invoice_load['result']['ID'],
                'title': invoice_load['result']['ORDER_TOPIC'],
                'currency': invoice_load['result']['CURRENCY'],
                'price': invoice_load['result']['PRICE'],
                'date_insert': invoice_load['result']['DATE_INSERT'],
                'date_paid': invoice_load['result']['DATE_PAYED'],
                'payed': invoice_load['result']['PAYED'],
                'responsible_email': invoice_load['result']['RESPONSIBLE_EMAIL'],
                'responsible_last_name': invoice_load['result']['RESPONSIBLE_LAST_NAME'],
                'responsible_name': invoice_load['result']['RESPONSIBLE_NAME'],
                'status_id': invoice_load['result']['STATUS_ID'],
                'product_rows': invoice_load['result']['PRODUCT_ROWS'],
            }
        # invoice = Invoice.objects.create()
        res = {
            'webhook': info['event'],
            'invoice': invoice
        }
        return render(request, "main.html", res)