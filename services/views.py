from django.shortcuts import render
from authentication.helpers.B24Webhook import B24_WEBHOOK
import requests
import json


def services(request):
    method = "crm.product.list"
    url = B24_WEBHOOK + method
    services_count = requests.get(url).json()['total']
    services_info = requests.get(url).json()['result']
    res = {
        'services_info': services_info,
        'services_count': services_count,
    }
    return render(request, "services/list.html", res)
