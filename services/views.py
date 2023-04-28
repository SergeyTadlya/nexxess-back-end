from django.shortcuts import render
from authentication.helpers.B24Webhook import set_webhook
import requests
import json


def services(request):
    method = "crm.product.list"
    url = set_webhook(method)
    services_count = requests.get(url).json()['total']
    services_info = requests.get(url).json()['result']
    context  = {
         'services_info': services_info,
         'services_count': services_count,
     }
    
    return render(request, "services/list.html", context)
