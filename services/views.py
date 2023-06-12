from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse

from authentication.helpers.B24Webhook import set_webhook
from authentication.models import B24keys
from invoices.models import Invoice, StripeSettings, LocalInvoice, Status

from tickets.models import Ticket
from .models import Service, ServiceCategory

from bitrix24 import Bitrix24, BitrixError

import datetime
import stripe
import time
import re


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
            section_list = bx24.callMethod('crm.productsection.list', order={'ID': "ASC"}, filter={"CATALOG_ID": 25},
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
                                                   select=["ID", "NAME", "PRICE", "CURRENCY_ID", "PROPERTY_143"])
                print(f'PRODUCT>>>>>>>>>>>{section_products}')
                min_price = 1000000
                products = []
                for product_b24 in section_products:

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
                        if product_b24["PROPERTY_143"] is None:
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
                                preview_text=product_b24["PROPERTY_143"]["value"],
                                price=format_price(product_b24["PRICE"]),
                                currency=product_b24["CURRENCY_ID"],
                                category=section_get,
                            )
                        product.save()
                    else:
                        if product_b24["PROPERTY_143"] is None:
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
                            product.preview_text = product_b24["PROPERTY_143"]["value"]
                            product.price = format_price(product_b24["PRICE"])
                            product.currency = product_b24["CURRENCY_ID"]
                            product.category = section_get
                        product.save()
                    products.append(product)

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
                                           select=["ID", "NAME", "PROPERTY_143", "PRICE", "CURRENCY_ID", "PROPERTY_144",
                                                   "DESCRIPTION", "SECTION_ID"])

        property_type = bx24.callMethod("crm.product.property.get", id=144)  # 100 - id custom field "type"
        description = []
        for products in section_products:
            stripe.api_key = StripeSettings.objects.all().first().secret_key
            price = format_price(products["PRICE"])
            stripe_response = stripe.Price.create(
                unit_amount=int(price) * 100,
                currency="usd",
                product_data={"name": products["NAME"]},
            )
            if products["PROPERTY_143"] is None:
                preview_text = ""
            else:
                preview_text = products["PROPERTY_143"]["value"]
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

            description_parts = products['DESCRIPTION'].split("• ")
            parts_array = [remove_html_tags(item.replace("&nbsp;", "").strip()) for item in description_parts if item.strip()]
            description.append({
                "ID": products["ID"],
                "DESCRIPTION": parts_array,
            })
            # User field "type" (need for template)
            property_type_id = products['PROPERTY_144']['value']
            property_type_name = property_type["VALUES"][property_type_id]["VALUE"]

            if (property_type_name != "Consultation"):
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
        return redirect('/services/')


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
                                                                'UF_CONTACT_ID': request.user.b24_contact_id,  # 1
                                                                'STATUS_ID': 'N',
                                                                'RESPONSIBLE_ID': 1,
                                                                'PAY_SYSTEM_ID': 3,
                                                                'DATE_PAY_BEFORE': tomorrow.strftime("%m/%d/%Y"),
                                                                "PRODUCT_ROWS": [
                                                                    {"ID": 0,
                                                                     "PRODUCT_ID": product.service_id,  # product.id
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
    property_type = bx24.callMethod("crm.product.property.get", id=144)  # 100 - id custom field "type"

    b24_service = []
    for service_id in purchased_services_id:
        section_products = bx24.callMethod('crm.product.list', order={'PRICE': "ASC"},
                                           filter={"ID": service_id},
                                           select=["ID", "NAME", "PROPERTY_143", "PRICE", "CURRENCY_ID", "PROPERTY_144",
                                                   "DESCRIPTION", "SECTION_ID"])
        for products in section_products:
            print(f'>>>>>>>>>PRODUCTS{products}')
            description_parts = products['DESCRIPTION'].split("<br>\n ")  ####### remove tags
            parts_array = [remove_html_tags(item) for item in description_parts]
            property_type_id = products['PROPERTY_144']['value']
            property_type_name = property_type["VALUES"][property_type_id]["VALUE"]
            pinned_invoice = Invoice.objects.filter(responsible=b24_contact_id, status=paid_invoice_status,
                                                    service_id=service_id).order_by('tracked_time')
            print(f'>>>>>>>>>PINNED{pinned_invoice}')
            if pinned_invoice.exists():
                pinned_invoice = pinned_invoice.first().invoice_id
                print(pinned_invoice)

            wasted_time = Ticket.objects.filter(responsible=b24_contact_id, pinned_invoice=pinned_invoice)
            print(f'wasted time:{wasted_time}')
            

            if wasted_time.exists():
                wasted_time = wasted_time.first().tracked_time
                print(wasted_time)
                print(f'>>>>>>>>>>>>>>>TIME{type(wasted_time)}')
            else:
                wasted_time = 0
            wasted_time = int(wasted_time) if wasted_time is not None else 0
            time_remaining_bx24 = ''.join(re.findall("[0-9]", products["PROPERTY_143"]["value"]))
            bought_time = int(time_remaining_bx24) * 3600
            print(f'wasted time>>>>{wasted_time}')
            time_remaining = bought_time - int(wasted_time)
            hours, minutes, seconds = time_remaining // 3600, (time_remaining % 3600) // 60, time_remaining % 60
            print(f'ws>>>>>>>>>>>>>>>>>>>>>>>>>{time_remaining}')
            Invoice.objects.update_or_create(invoice_id=pinned_invoice,
                                             defaults={"tracked_time": wasted_time})
            b24_service.append({
                "ID": products["ID"],
                "NAME": products["NAME"],
                "DESCRIPTION": parts_array,
                "PRICE": products["PRICE"],
                "CATEGORY": property_type_name,
                "TIME_REMAINING": f"{hours:02d}:{minutes:02d}:{seconds:02d}",
            })
    b24_domain = B24keys.objects.order_by("id").first().domain[:-1]
    print(f'b24_service>>>>>>>>>>>>>>{b24_service}')
    context = {
        'b24_domain': b24_domain,
        'b24_service': b24_service
    }
    return render(request, "services/my_services.html", context=context)
