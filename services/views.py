from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from bitrix24 import Bitrix24, BitrixError
from requests import Response

from authentication.helpers.B24Webhook import set_webhook
from invoices.models import Invoice, StripeSettings, LocalInvoice
from telegram_bot.models import User
from .models import Service
from . import urls

import datetime
import requests
import stripe
import time
import json
import re



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
    if request.user.is_authenticated and request.user.google_auth or request.user.is_superuser:
        try:
            url = set_webhook()
            bx24 = Bitrix24(url)
            section_list = bx24.callMethod('crm.productsection.list', order={'ID': "ASC"}, filter={"CATALOG_ID": 14}, select={"ID", "NAME", "CODE",
                                                                                                   "DESCRIPTION"})
            print(section_list)
            sections = []
            for section in section_list:
                section_products = bx24.callMethod('crm.product.list', order={'ID': "ASC"},
                                                   filter={"SECTION_ID": section["ID"]},
                                                   select=["ID", "NAME", "PROPERTY_98", "PRICE", "CURRENCY_ID"])
                min_price = 1000000
                products = []
                for product_b24 in section_products:
                    # print(product_b24)

                    if min_price > float(product_b24["PRICE"]):
                        min_price = float(product_b24["PRICE"])
                    product = Service.objects.filter(service_id=product_b24['ID'])
                    if len(product) == 0:
                        stripe.api_key = StripeSettings.objects.all().first().secret_key
                        price = format_price(product_b24["PRICE"])
                        stripe_response = stripe.Price.create(
                            unit_amount=int(price)*100,
                            currency="usd",
                            product_data={"name": product_b24["NAME"]},
                        )
                        if product_b24["PROPERTY_98"] is None:
                            product = Service.objects.create(
                                service_id=product_b24["ID"],
                                stripe_id=stripe_response.id,
                                title=product_b24["NAME"],
                                price=format_price(product_b24["PRICE"]),
                                currency=product_b24["CURRENCY_ID"],
                            )
                        else:
                            product = Service.objects.create(
                                service_id=product_b24["ID"],
                                stripe_id=stripe_response.id,
                                title=product_b24["NAME"],
                                preview_text=product_b24["PROPERTY_98"]["value"],
                                price=format_price(product_b24["PRICE"]),
                                currency=product_b24["CURRENCY_ID"],
                            )
                        product.save()
                    else:
                        if product_b24["PROPERTY_98"] is None:
                            product = Service.objects.get(id=product.first().id)
                            product.service_id = product_b24["ID"]
                            product.title = product_b24["NAME"]
                            product.price = format_price(product_b24["PRICE"])
                            product.currency = product_b24["CURRENCY_ID"]
                        else:
                            product = Service.objects.get(id=product.first().id)
                            product.service_id = product_b24["ID"]
                            product.title = product_b24["NAME"]
                            product.preview_text = product_b24["PROPERTY_98"]["value"]
                            product.price = format_price(product_b24["PRICE"])
                            product.currency = product_b24["CURRENCY_ID"]
                        product.save()
                    products.append(product)
                    # print(product_b24)
                test = {
                    'products': products,
                    'min_price': min_price,
                    'sections_title': section["NAME"],
                    'section_id': section["ID"]
                }
                sections.append(test)
                # print(sections)

            context = {
                'sections': sections,
                'services_count': len(products),
            }
            print(context)
            return render(request, "services/list.html", context=context)
        except:
            context = {}
            return render(request, "services/list.html", context=context)



@login_required(login_url='/accounts/login/')
def product_detail(request, id):
    try:
        print(id)
        url = set_webhook()
        bx24 = Bitrix24(url)
        section = bx24.callMethod('crm.productsection.list', order={'ID': "ASC"},
                                  filter={"ID": id},
                                  select={"ID", "NAME", "CODE"})
        print(section)
        sections = []
        section_products = bx24.callMethod('crm.product.list', order={'PRICE': "ASC"},
                                           filter={"SECTION_ID": id},
                                           select=["ID", "NAME", "PROPERTY_98", "PRICE", "CURRENCY_ID"])
        # service = get_object_or_404(Service, id=id)
        context = {
            'services': section_products,
            'section_title': section[0]["NAME"]
        }
        return render(request, "services/consultation.html", context=context)

    except:
        return redirect('services')


@login_required(login_url='/accounts/login/')
def service_1(request):
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
                    title_description=product_data.get('DESCRIPTION'),
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
        return render(request, "services/consultation.html", context=context)
    except:
        context = {}
    return render(request, 'services/consultation.html', context=context)



def service_2(request):
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
                    title_description=product_data.get('DESCRIPTION'),
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
        return render(request, "services/service2.html", context=context)
    except:
        context = {}
    return render(request, 'services/service2.html', context=context)





def service_3(request):
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
                    title_description=product_data.get('DESCRIPTION'),
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
        return render(request, "services/service3.html", context=context)
    except:
        context = {}
    return render(request, 'services/service3.html', context=context)






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

        time.sleep(3)
        LocalInvoice.objects.create(b24_invoice_id=invoice_id, stripe_price_id=product.stripe_id)
        invoice = Invoice.objects.get(invoice_id=invoice_id)
    except BitrixError as message:
        print(message)

    return JsonResponse({'invoice_id': str(invoice.id)})
