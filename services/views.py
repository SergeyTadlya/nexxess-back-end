from django.shortcuts import render, redirect, get_object_or_404
from authentication.helpers.B24Webhook import set_webhook
from django.contrib.auth.decorators import login_required
from .models import Service
from django.shortcuts import render
import requests
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
    try:
        method = "crm.product.list"
        url = set_webhook(method)
        response = requests.get(url)
        products_data = response.json().get('result', [])
        products = []
        for product_data in products_data:
            product = Service.objects.update_or_create(
                service_id=product_data.get('ID'),
                defaults={
                    'title': product_data.get('NAME'),
                    'service_id':  product_data.get('ID'),
                    'title_description': clean_and_shorten_text(product_data.get('DESCRIPTION')),
                    'price': format_price(product_data.get('PRICE')),
                    'currency': product_data.get('CURRENCY_ID'),


                }
            )[0]
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
