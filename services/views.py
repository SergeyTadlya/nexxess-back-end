from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from bitrix24 import Bitrix24, BitrixError
from requests import Response
from authentication.helpers.B24Webhook import set_webhook
from invoices.models import Invoice, StripeSettings, LocalInvoice, Status
from telegram_bot.models import User
from .models import Service, ServiceCategory
from . import urls
import datetime
import requests
import stripe
import time
import json
import re
from authentication.models import B24keys


def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def clean_and_shorten_text(text):

    cleaned_text = re.sub('<[^<]+?>', '', text)

    if len(cleaned_text) > 200:
        cleaned_text = cleaned_text[:200] + '...'

    return cleaned_text


def format_price(price):
    price = str(price)
    price = price.rstrip('0').rstrip('.') if '.' in price else price

    return f'{price}' if price else ''


@login_required(login_url='/accounts/login/')
def services(request):
    if request.user.is_authenticated and request.user.google_auth or request.user.is_superuser:
        try:
            url = set_webhook()
            bx24 = Bitrix24(url)
            section_list = bx24.callMethod('crm.productsection.list', order={'ID': "ASC"}, filter={"CATALOG_ID": 14},
                                           select={"ID", "NAME", "CODE",
                                                   "DESCRIPTION"})
            sections = []
            for section in section_list:
                section_get, section_create = ServiceCategory.objects.get_or_create(
                    category_b24_id=section["ID"],
                    defaults={'category_name': section["NAME"]},
                )
                section_products = bx24.callMethod('crm.product.list', order={'ID': "ASC"},
                                                   filter={"SECTION_ID": section["ID"]},
                                                   select=["ID", "NAME", "PROPERTY_98", "PRICE", "CURRENCY_ID",
                                                           "PROPERTY_44"])
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
                            unit_amount=int(price) * 100,
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
                                category=section_get,
                            )
                        else:
                            product = Service.objects.create(
                                service_id=product_b24["ID"],
                                stripe_id=stripe_response.id,
                                title=product_b24["NAME"],
                                preview_text=product_b24["PROPERTY_98"]["value"],
                                price=format_price(product_b24["PRICE"]),
                                currency=product_b24["CURRENCY_ID"],
                                category=section_get,
                            )
                        product.save()
                    else:
                        if product_b24["PROPERTY_98"] is None:
                            product = Service.objects.get(id=product.first().id)
                            product.service_id = product_b24["ID"]
                            product.title = product_b24["NAME"]
                            product.price = format_price(product_b24["PRICE"])
                            product.currency = product_b24["CURRENCY_ID"]
                            product.category = section_get
                        else:
                            product = Service.objects.get(id=product.first().id)
                            product.service_id = product_b24["ID"]
                            product.title = product_b24["NAME"]
                            product.preview_text = product_b24["PROPERTY_98"]["value"]
                            product.price = format_price(product_b24["PRICE"])
                            product.currency = product_b24["CURRENCY_ID"]
                            product.category = section_get
                        product.save()
                    products.append(product)
                    # print(product_b24)

                if not products:
                    set_min_price = 0
                else:
                    set_min_price = min_price
                test = {
                    'products': products,
                    'min_price': set_min_price,
                    'sections_title': section["NAME"],
                    'section_id': section["ID"]
                }
                sections.append(test)
                # print(sections)

            context = {
                'sections': sections,
                'services_count': len(products),
            }
        except:
            context = {}

        return render(request, "services/list.html", context=context)


@login_required(login_url='/accounts/login/')
def product_detail(request, id):
    try:
        url = set_webhook()
        bx24 = Bitrix24(url)
        section = bx24.callMethod('crm.productsection.list', order={'ID': "ASC"},
                                  filter={"ID": id},
                                  select={"ID", "NAME", "CODE"})
        section_get, section_create = ServiceCategory.objects.get_or_create(
            category_b24_id=section[0]["ID"],
            defaults={'category_name': section[0]["NAME"]},
        )

        sections = []
        section_products = bx24.callMethod('crm.product.list', order={'PRICE': "ASC"},
                                           filter={"SECTION_ID": id},
                                           select=["ID", "NAME", "PROPERTY_98", "PRICE", "CURRENCY_ID", "PROPERTY_100", "DESCRIPTION", "SECTION_ID", "PROPERTY_MORE_PHOTO"])
        # service = get_object_or_404(Service, id=id)

        property_type = bx24.callMethod("crm.product.property.get", id=100) # 100 - id custom field "type"
        description = []
        for products in section_products:
            stripe.api_key = StripeSettings.objects.all().first().secret_key
            price = format_price(products["PRICE"])
            stripe_response = stripe.Price.create(
                unit_amount=int(price) * 100,
                currency="usd",
                product_data={"name": products["NAME"]},
            )
            if products["PROPERTY_98"] is None:
                preview_text = ""
            else:
                preview_text = products["PROPERTY_98"]["value"]
            defaults = {
                'stripe_id': stripe_response.id,
                'title': products["NAME"],
                'preview_text': preview_text,
                'price': price,
                'currency': products["CURRENCY_ID"],
                'category': section_get,
            }

            service_get, service_create = Service.objects.get_or_create(
                service_id=products["ID"],
                defaults=defaults
            )

            # description convertation for template
            # description_parts = products['DESCRIPTION'].split("•")
            # parts_array = []
            # for description_part in description_parts:
            #     if description_part != "":
            #         parts_array.append(description_part.strip().replace('<br>', ''))

            description_parts = products['DESCRIPTION'].split("<br>\n ")
            parts_array = [remove_html_tags(item) for item in description_parts]
            description.append({
                "ID": products["ID"],
                "DESCRIPTION": parts_array,
            })
            # user field "type" (need for template)
            property_type_id = products['PROPERTY_100']['value']
            property_type_name = property_type["VALUES"][property_type_id]["VALUE"]
            if(property_type_name != "Consultation"):
                template = "services/other.html"
            else:
                template = "services/consultation.html"

        b24_domain = B24keys.objects.order_by("id").first().domain[:-1]
        context = {
            'b24_domain': b24_domain,
            'services': section_products,
            'services_description': description,
            'section_title': section[0]["NAME"]
        }
        return render(request, template, context=context)

    except:
        return redirect('/')


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
                                                   'UF_CONTACT_ID': request.user.b24_contact_id, #1
                                                   'STATUS_ID': 'N',
                                                   'RESPONSIBLE_ID': 1,
                                                   'PAY_SYSTEM_ID': 4,
                                                   'DATE_PAY_BEFORE': tomorrow.strftime("%m/%d/%Y"),
                                                   "PRODUCT_ROWS": [
                                                       {"ID": 0,
                                                        "PRODUCT_ID": product.service_id, #product.id
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


@login_required(login_url='/accounts/login/')
def my_services(request):
    paid_invoice_status = Status.objects.get(abbreviation="P", value="Paid")
    b24_contact_id = request.user.b24_contact_id
    invoices = Invoice.objects.filter(responsible=b24_contact_id, status=paid_invoice_status)

    # get purchased services from invoices
    purchased_services_id = []
    for invoice in invoices:
        services_list = Service.objects.filter(service_id=invoice.service_id)[0]
        purchased_services_id.append(services_list.service_id)

    url = set_webhook()
    bx24 = Bitrix24(url)
    property_type = bx24.callMethod("crm.product.property.get", id=100)  # 100 - id custom field "type"

    b24_service = []
    for service_id in purchased_services_id:
        section_products = bx24.callMethod('crm.product.list', order={'PRICE': "ASC"},
                                           filter={"ID": service_id},
                                           select=["ID", "NAME", "PROPERTY_98", "PRICE", "CURRENCY_ID", "PROPERTY_100",
                                                   "DESCRIPTION", "SECTION_ID", "PROPERTY_44"])
        for products in section_products:
            description_parts = products['DESCRIPTION'].split("<br>\n ")
            parts_array = [remove_html_tags(item) for item in description_parts]

            property_type_id = products['PROPERTY_100']['value']
            property_type_name = property_type["VALUES"][property_type_id]["VALUE"]

            b24_service.append({
                "ID": products["ID"],
                "NAME": products["NAME"],
                "DESCRIPTION": parts_array,
                "IMAGE": products["PROPERTY_44"],
                "PRICE": products["PRICE"],
                "CATEGORY": property_type_name,
            })

    b24_domain = B24keys.objects.order_by("id").first().domain[:-1]
    context = {
        'b24_domain': b24_domain,
        'b24_service': b24_service
    }
    return render(request, "services/my_services.html", context=context)
