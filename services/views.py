from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from requests import Response

from authentication.helpers.B24Webhook import set_webhook
from django.contrib.auth.decorators import login_required

from invoices.models import Invoice, StripeSettings, LocalInvoice
from telegram_bot.models import User
from .models import Service
from django.shortcuts import render
import requests
import json
import re
import time
import datetime
import stripe

from bitrix24 import Bitrix24, BitrixError


def format_price(price):
    price = str(price)
    price = price.rstrip('0').rstrip('.') if '.' in price else price

    return f'{price}' if price else ''

def clean_and_shorten_text(text):

    cleaned_text = re.sub('<[^<]+?>', '', text)

    if len(cleaned_text) > 200:
        cleaned_text = cleaned_text[:200] + '...'

    return cleaned_text



@login_required(login_url='/accounts/login/')
def services(request):
    try:
        method = "crm.product.list"
        url = set_webhook(method)
        response = requests.get(url)
        products_data = response.json().get('result', [])
        products = []
        for product_data in products_data:
            # stripe_response = stripe.Product.create(name="Gold Special")
            product = Service.objects.filter(service_id=product_data.get('ID'))
            if len(product) == 0:
                stripe.api_key = StripeSettings.objects.all().first().secret_key
                price = format_price(product_data.get('PRICE'))
                print(int(price)*100)
                stripe_response = stripe.Price.create(
                    unit_amount=int(price)*100,
                    currency="usd",
                    product_data={"name": product_data.get('NAME')},
                )
                product = Service.objects.create(
                    service_id=product_data.get('ID'),
                    stripe_id=stripe_response.id,
                    title=product_data.get('NAME'),
                    title_description=clean_and_shorten_text(product_data.get('DESCRIPTION')),
                    price=format_price(product_data.get('PRICE')),
                    currency=product_data.get('CURRENCY_ID'),
                )
                product.save()
            else:
                product = Service.objects.get(id=product.first().id)
                product.service_id = product_data.get('ID')
                product.title = product_data.get('NAME')
                product.title_description = clean_and_shorten_text(product_data.get('DESCRIPTION'))
                product.price = format_price(product_data.get('PRICE'))
                product.currency = product_data.get('CURRENCY_ID')
                product.save()
            products.append(product)

        context = {
            'services_info': products,
            'services_count': len(products),
        }
        return render(request, "services/list.html", context=context)
    except:
        context = {}
        return render(request, "services/list.html", context=context)


@login_required(login_url='/accounts/login/')
def product_detail(request, id):
    try:
        service = get_object_or_404(Service, id=id)
        context = {
            'service': service,
        }
        return render(request, "services/about-service.html", context=context)

    except:
        return redirect('services')


@login_required(login_url='/accounts/login/')
@csrf_exempt
def create_invoice(request):
    method = "crm.product.list"
    url = set_webhook(method)
    b24_product_id = request.POST["b24_product_id"]
    product = Service.objects.get(service_id=request.POST["b24_product_id"])
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    bx24 = Bitrix24(url)
    try:
        invoice_id = bx24.callMethod('crm.invoice.add', fields={'ORDER_TOPIC': "Invoice - " + product.title,
                                                               'PERSON_TYPE_ID': 1,
                                                               'UF_CONTACT_ID': request.user.b24_contact_id,
                                                               'STATUS_ID': 'N',
                                                               'RESPONSIBLE_ID': 1,
                                                               'PAY_SYSTEM_ID': 3,
                                                               'DATE_PAY_BEFORE': tomorrow.strftime("%m/%d/%Y"),
                                                               "PRODUCT_ROWS": [
                                                                   {"ID": 0,
                                                                    "PRODUCT_ID": product.id,
                                                                    "PRODUCT_NAME": product.title,
                                                                    "QUANTITY": 1,
                                                                    "PRICE": product.price},
                                                               ]})

        time.sleep(5)
        LocalInvoice.objects.create(b24_invoice_id=invoice_id,stripe_price_id=product.stripe_id)

    except BitrixError as message:
        print(message)

    return JsonResponse({'invoice_id': str(invoice_id)})
