from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import JsonResponse

from authentication.helpers.B24Webhook import set_webhook
from invoices.views import format_date
from .models import Ticket, TicketStatus

from datetime import datetime

import requests
import json
import time

from bitrix24 import Bitrix24
import xml.etree.ElementTree as ET


def check_and_shorten_string(string):
    if len(string) > 20:
        string = string[:20] + '...'
    return string


@login_required(login_url='/accounts/login/')
def tasks(request):
    all_user_tasks = Ticket.objects.all().order_by('-created_at') if request.user.is_superuser \
        else Ticket.objects.filter(responsible=str(request.user.b24_contact_id)).order_by('-created_at')

    tasks_array = list()
    tasks_dates = list()
    tasks_statuses = list()

    all_statuses = TicketStatus.objects.all()
    statuses = (status.name for status in all_statuses)
    statuses_quantity = (value - value for value in range(len(all_statuses)))
    statuses_number = {key: value for key, value in zip(statuses, statuses_quantity)}

    date_count = 0
    for index, task in enumerate(all_user_tasks):
        statuses_number[task.status.name] = 1 if task.status.name not in statuses_number.keys() \
            else statuses_number[task.status.name] + 1

        tasks_array.append({
            'id': task.task_id,
            'title': check_and_shorten_string(task.ticket_title),
            'status': task.status,
            'created_at': format_date(task.created_at),
            'deadline': format_date(task.deadline),
            'is_opened': task.is_opened,
        })

        if not tasks_array[date_count]['created_at'] == format_date(task.created_at) or index == 0:
            date_count = index
            tasks_array[index]['more_one'] = True
        else:
            tasks_array[index]['more_one'] = False

    for index, (status_name, status_number) in enumerate(statuses_number.items()):
        tasks_statuses.append({
            'id': 'status' + str(index + 1),
            'name': status_name,
            'number': status_number
        })

    paginator = Paginator(tasks_array, 10)
    page = request.GET.get('page', 1)

    try:
        tasks_array = paginator.page(page)
    except PageNotAnInteger:
        tasks_array = paginator.page(1)
    except EmptyPage:
        tasks_array = paginator.page(paginator.num_pages)

    context = {
        'tasks': tasks_array,
        "tasks_dates": tasks_dates,
        'tasks_statuses': tasks_statuses,
        'tasks_number': len(all_user_tasks),
        'statuses_amount': len(tasks_statuses),
    }

    return render(request, "tickets/tickets.html", context)


def ajax_tasks_filter(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        if request.method == 'POST':
            data = json.load(request)
            statuses = [keys for keys in data if data[keys] is True]

            all_user_tasks = Ticket.objects.all().order_by('-created_at') if request.user.is_superuser \
                else Ticket.objects.filter(responsible=str(request.user.b24_contact_id)).order_by('-created_at')

            tasks_array = list()
            tasks_dates = list()

            if 'ascending' in data.keys():
                all_user_tasks = all_user_tasks.order_by(data['ascending'])
            elif 'descending' in data.keys():
                all_user_tasks = all_user_tasks.order_by('-' + data['descending'])

            if statuses:
                all_user_tasks = all_user_tasks.filter(status__name__in=statuses)

            if data['from_date'] and data['to_date']:
                all_user_tasks = all_user_tasks.filter(
                    created_at__gte=datetime.strptime(data['from_date'], '%B.%d.%Y'),
                    created_at__lte=datetime.strptime(data['to_date'], '%B.%d.%Y')
                )

            if data['local_search']:
                all_user_tasks = all_user_tasks.filter(
                    Q(task_id__icontains=data['local_search']) |
                    Q(ticket_title__icontains=data['local_search']) |
                    Q(status__name__icontains=data['local_search']) |
                    Q(created_at__icontains=data['local_search']) |
                    Q(deadline__icontains=data['local_search'])
                )

            date_count = 0
            for index, task in enumerate(all_user_tasks):
                tasks_array.append({
                    'id': task.task_id,
                    'title': check_and_shorten_string(task.ticket_title),
                    'status_name': task.status.name,
                    'status_color': task.status.color,
                    'created_at': format_date(task.created_at),
                    'deadline': format_date(task.deadline),
                    'is_opened': task.is_opened,
                })

                if index == 0 or not tasks_array[date_count]['created_at'] == format_date(task.created_at):
                    date_count = index
                    tasks_array[index]['more_one'] = True
                else:
                    tasks_array[index]['more_one'] = False

            paginator = Paginator(tasks_array, 10)
            page = request.GET.get('page', 1)

            try:
                tasks_array = paginator.page(page)
            except PageNotAnInteger:
                tasks_array = paginator.page(1)
            except EmptyPage:
                tasks_array = paginator.page(paginator.num_pages)

            has_next = tasks_array.has_next()
            has_previous = tasks_array.has_previous()
            has_other_pages = tasks_array.has_other_pages()
            page_range = list(tasks_array.paginator.page_range)
            next_page = tasks_array.number + 1 if tasks_array.has_next() else tasks_array.number
            previous_page = tasks_array.number - 1 if tasks_array.has_previous() else tasks_array.number

            if data['showing_amount']:
                # showing_amount = int(data['showing_amount']) if not data['showing_amount'] == 'All' else len(invoices_array)
                showing_amount = 100
                tasks_array = tasks_array[:showing_amount] if showing_amount >= 10 else tasks_array

            response = {
                'tasks': [tasks_array],
                "tasks_dates": tasks_dates,
                'tasks_number': len(all_user_tasks),
                'showing_amount': str(len(all_user_tasks)),
                'has_next': has_next,
                'has_previous': has_previous,
                'has_other_pages': has_other_pages,
                'page_range': page_range,
                'next_page': next_page,
                'previous_page': previous_page
            }

            return JsonResponse(response)


def task_detail(request, id):
    task = Ticket.objects.get(task_id=str(id))
    if request.user.is_superuser or int(task.responsible) == request.user.b24_contact_id:
        if not request.user.is_superuser:
            Ticket.objects.filter(id=id).update(is_opened=True)
            status_closed = Ticket.objects.filter(responsible=str(request.user.b24_contact_id),  status__name='Closed').count()
            status_overdue = Ticket.objects.filter(responsible=str(request.user.b24_contact_id),  status__name='Overdue').count()
            status_ongoin = Ticket.objects.filter(responsible=str(request.user.b24_contact_id),  status__name='Ongoing').count()
        else:
            status_closed = 0
            status_overdue = 0
            status_ongoin = 0

        res = {
            'task': task,
            'status_closed': status_closed,
            'status_overdue': status_overdue,
            'status_ongoin': status_ongoin,
        }
        return render(request, "tickets/detail.html", res)
    else:
        return redirect('/tickets/')


def create_bitrix_task(request):
    if request.method == 'POST':
        responsible = str(request.user.b24_contact_id)
        task_name = request.POST.get('task_name')
        task_description = request.POST.get('task_description')
        task_deadline = request.POST.get('task_deadline') if not 'NoneType' else datetime.today().strftime("%b.%d.%Y")
        print('type >>>>>', type(task_deadline))
        print('date>>>>>>>>', task_deadline)

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
            print('test123 create task')
            response_data = json.loads(response.content)
            task_id = response_data['result']['task']['id']
            print('response task_id', task_id)

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
            'status': task.status.name,

        })

    context = {
        "tasks": tasks,
        'tasks_number': len(tasks),
    }
    # url = set_webhook()
    # bx24 = Bitrix24(url)
    # ticket = bx24.callMethod('tasks.task.list', order={'ID': "ASC"},
    #                                        filter={"ID": 550, "LOAD_TAGS": "Y"},
    #                                        select=["ID", "LOAD_TAGS"])

    # url = set_webhook("task.item.gettags.xml?TASK_ID=550")
    # response = requests.get(url)
    # root = ET.fromstring(response.content)
    # items = root.findall('.//item')
    # item_values = [item.text for item in items]
    # print('response_data 550', item_values)

    # url = set_webhook("tasks.task.update?taskId=556&fields[TAGS]=tag_one,tag_two")
    # response = requests.post(url)
    # print('response', response)
    return render(request, 'tickets/list.html', context)
