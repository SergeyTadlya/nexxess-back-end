from django.shortcuts import render, redirect

from authentication.helpers.B24Webhook import set_webhook
from invoices.views import format_date

from .models import Ticket

import requests
import time


def check_and_shorten_string(string):
    if len(string) > 20:
        string = string[:20] + '...'
    return string


def tasks(request):
    all_user_tasks = Ticket.objects.all().order_by('-created_at') if request.user.is_superuser \
        else Ticket.objects.filter(responsible=str(request.user.b24_contact_id)).order_by('-created_at')

    tasks_array = list()
    tasks_statuses = list()

    for task in all_user_tasks:
        tasks_array.append({
            'id': task.task_id,
            'title': check_and_shorten_string(task.ticket_title),
            'created_at': format_date(task.created_at),
            'deadline': format_date(task.deadline),
            'is_opened': task.is_opened,
            'status': task.status,
        })

    context = {
        "tasks": tasks_array,
        'tasks_number': len(tasks_array),
    }
    return render(request, "tickets/tickets.html", context)


def task_detail(request, id):
    task = Ticket.objects.get(id=id)
    if request.user.is_superuser or task.responsible == request.user.b24_contact_id:
        # апдейт задачі, коли менеджер відкрив її (це щоб на головній сторінці, вона зникла із списка нових задач)
        if not request.user.is_superuser:
            Ticket.objects.filter(id=id).update(is_opened=True)

        res = {
            'task': task,
        }
        return render(request, "tickets/tickets.html", res)
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
    tasks = []  # вместо tasks_array

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
