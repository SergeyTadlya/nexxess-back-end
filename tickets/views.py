from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse

from bitrix24 import Bitrix24, BitrixError

from authentication.helpers.B24Webhook import set_webhook
from authentication.models import B24keys

from .models import Ticket
from .urls import *

import requests
from datetime import datetime
import json
import time


def format_date(date):
    return date.strftime('%d %b %Y') if date else ''

def check_and_shorten_string(string):
    if len(string) > 20:
        string = string[:20] + '...'
    return string



def tasks(request):
    if request.user.is_authenticated and request.user.google_auth or request.user.is_superuser:
        tasks_list = Ticket.objects.all() if request.user.is_superuser else Ticket.objects.filter(responsible=str(request.user.b24_contact_id))
        tasks = []

        for task in tasks_list:

            tasks.append({
                'id': task.task_id,
                'title': check_and_shorten_string(task.ticket_title),
                'created_at': format_date(task.created_at),
                'deadline': format_date(task.deadline),
                'is_opened': task.is_opened,
                'status': task.status,

            })

        context = {
            "tasks": tasks,
            'tasks_number': len(tasks),
        }
        return render(request, "tickets/tickets.html", context)
    else: return redirect('authentication:main')


def task_detail(request, id):
    task = Ticket.objects.get(task_id=str(id))
    if request.user.is_superuser or task.responsible == str(request.user.b24_contact_id):
        if not request.user.is_superuser:
            Ticket.objects.filter(id=id).update(is_opened=True)

        res = {
            'task': task,
        }
        return render(request, "tickets/detail.html", res)
    else:
        return redirect('/tickets/')


def create_bitrix_task(request):
    if request.method == 'POST':
        responsible = str(request.user.b24_contact_id)
        task_name = request.POST.get('task_name')
        task_description = request.POST.get('task_description')
        task_deadline = request.POST.get('task_deadline')
        try:

            method = "tasks.task.add"
            url = set_webhook(method)

            payload = {
                'fields': {
                    'TITLE': task_name,
                    'DESCRIPTION': task_description,
                    'DEADLINE': task_deadline,
                    'CREATED_BY': 2,
                    'RESPONSIBLE_ID': 1,
                    'PRIORITY': 2,
                    'ALLOW_CHANGE_DEADLINE': 1,
                    'UF_CRM_TASK': {
                        "0": 'C_' + responsible,  # bitrix24_id
                        }
                    }
                }
            response = requests.post(url, json=payload)
            print(response)
            task_id = response.json().get('result')
            print(f'task_id{task_id}')

            if response.status_code == 200:
                time.sleep(5)
                return redirect('tickets:tasks')

        except Exception as e:
            print(e)

    return render(request, 'tickets/tickets.html')


def task_data(request):
    tasks_list = Ticket.objects.all() if request.user.is_superuser else Ticket.objects.filter(
        responsible=str(request.user.b24_contact_id))
    tasks = []

    for task in tasks_list:
        tasks.append({
            'id': task.task_id,
            'title': check_and_shorten_string(task.ticket_title),
            'created_at': format_date(task.created_at),
            'deadline': format_date(task.deadline),
            'is_opened': task.is_opened,
            'status': task.status,

        })

    context = {
        "tasks": tasks,
        'tasks_number': len(tasks),
    }
    return render(request, 'tickets/list.html', context)
