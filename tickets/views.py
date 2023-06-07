from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import JsonResponse

from authentication.helpers.B24Webhook import set_webhook
from invoices.views import format_date
from invoices.models import *
from .models import Ticket, TicketStatus, TicketComments
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import time

from bitrix24 import Bitrix24
import xml.etree.ElementTree as ET
from nexxes_proj import settings
import os
import base64


from bs4 import BeautifulSoup
from authentication.models import B24keys
import re
def check_and_shorten_string(string):
    if len(string) > 20:
        string = string[:20] + '...'
    return string


@login_required(login_url='/accounts/login/')
def tasks(request):
    # Get all user tickets and sorting by created date
    all_user_tasks = Ticket.objects.all().order_by('-created_at') if request.user.is_superuser \
        else Ticket.objects.filter(responsible=str(request.user.b24_contact_id)).order_by('-created_at')

    # Get all existing statuses for user tickets
    all_statuses = TicketStatus.objects.all()
    statuses = (status.name for status in all_statuses)
    statuses_quantity = (value - value for value in range(len(all_statuses)))
    statuses_number = {key: value for key, value in zip(statuses, statuses_quantity)}
    bought_services = Invoice.objects.filter(responsible=str(request.user.b24_contact_id), status__value='Paid')

    # Iterate through the array and put every specified field into a list
    date_count = 0
    tasks_array = list()
    for index, task in enumerate(all_user_tasks):
        statuses_number[task.status.name] = 1 if task.status.name not in statuses_number.keys() \
            else statuses_number[task.status.name] + 1

        ticket = Ticket.objects.get(task_id=task.task_id)
        new_comment = TicketComments.objects.filter(ticket=ticket, is_opened=False).count()
        tasks_array.append({
            'id': task.task_id,
            'title': check_and_shorten_string(task.ticket_title),
            'status': task.status,
            'created_at': format_date(task.created_at),
            'deadline': format_date(task.deadline),
            'is_opened': task.is_opened,
            'new_comment': new_comment,
        })

        # Condition for removing bugs with pagination
        if not tasks_array[date_count]['created_at'] == format_date(task.created_at) or index == 0:
            date_count = index
            tasks_array[index]['more_one'] = True
        else:
            tasks_array[index]['more_one'] = False

    # Get all existing statuses and their quantity for user tickets
    tasks_statuses = list()
    for index, (status_name, status_number) in enumerate(statuses_number.items()):
        tasks_statuses.append({
            'id': 'status' + str(index + 1),
            'name': status_name,
            'number': status_number
        })

    # Pagination for tickets
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
        'tasks_statuses': tasks_statuses,
        'tasks_number': len(all_user_tasks),
        'statuses_amount': len(tasks_statuses),
        'bought_services': bought_services,
    }

    return render(request, "tickets/tickets.html", context)


def ajax_tasks_filter(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        if request.method == 'POST':
            data = json.load(request)
            statuses = [keys for keys in data if data[keys] is True]

            # Get all user tickets and sorting by created date
            all_user_tasks = Ticket.objects.all().order_by('-created_at') if request.user.is_superuser \
                else Ticket.objects.filter(responsible=str(request.user.b24_contact_id)).order_by('-created_at')

            # Ascending or Descending filtering by the field selected by the user
            if 'ascending' in data.keys():
                all_user_tasks = all_user_tasks.order_by(data['ascending'])
            elif 'descending' in data.keys():
                all_user_tasks = all_user_tasks.order_by('-' + data['descending'])

            # Tickets existing statuses
            if statuses:
                all_user_tasks = all_user_tasks.filter(status__name__in=statuses)

            # Calendar filtering
            if data['from_date'] and data['to_date']:
                all_user_tasks = all_user_tasks.filter(
                    created_at__gte=datetime.strptime(data['from_date'] + 'T00:00:00', '%B.%d.%YT%H:%M:%S'),
                    created_at__lte=datetime.strptime(data['to_date'] + 'T23:59:59', '%B.%d.%YT%H:%M:%S')
                )
            elif data['from_date']:
                all_user_tasks = all_user_tasks.filter(
                    created_at__gte=datetime.strptime(data['from_date'] + 'T00:00:00', '%B.%d.%YT%H:%M:%S'),
                )
            elif data['to_date']:
                all_user_tasks = all_user_tasks.filter(
                    created_at__lte=datetime.strptime(data['to_date'] + 'T23:59:59', '%B.%d.%YT%H:%M:%S')
                )

            # Local search on ticket page
            if data['local_search']:
                all_user_tasks = all_user_tasks.filter(
                    Q(task_id__icontains=data['local_search']) |
                    Q(ticket_title__icontains=data['local_search']) |
                    Q(status__name__icontains=data['local_search']) |
                    Q(created_at__icontains=data['local_search']) |
                    Q(deadline__icontains=data['local_search'])
                )

            # Iterate through the array and put everything into a list
            date_count = 0
            tasks_array = list()
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

                # Condition for removing bugs with pagination
                if index == 0 or not tasks_array[date_count]['created_at'] == format_date(task.created_at):
                    date_count = index
                    tasks_array[index]['more_one'] = True
                else:
                    tasks_array[index]['more_one'] = False

            # Pagination for tickets
            paginator = Paginator(tasks_array, 10)
            page = request.GET.get('page', 1)

            try:
                tasks_array = paginator.page(page)
            except PageNotAnInteger:
                tasks_array = paginator.page(1)
            except EmptyPage:
                tasks_array = paginator.page(paginator.num_pages)

            # Get all pagination data for converting to json format
            has_next = tasks_array.has_next()
            has_previous = tasks_array.has_previous()
            has_other_pages = tasks_array.has_other_pages()
            page_range = list(tasks_array.paginator.page_range)
            next_page = tasks_array.number + 1 if tasks_array.has_next() else tasks_array.number
            previous_page = tasks_array.number - 1 if tasks_array.has_previous() else tasks_array.number

            # Not working yet
            if data['showing_amount']:
                # showing_amount = int(data['showing_amount']) if not data['showing_amount'] == 'All' else len(tickets_array)
                showing_amount = 100
                tasks_array = tasks_array[:showing_amount] if showing_amount >= 10 else tasks_array

            response = {
                'tasks': [tasks_array],
                'tasks_number': len(all_user_tasks),
                'showing_amount': str(len(all_user_tasks)),
                'page_range': page_range,
                'has_next': has_next,
                'has_previous': has_previous,
                'has_other_pages': has_other_pages,
                'next_page': next_page,
                'previous_page': previous_page
            }

            return JsonResponse(response)


def task_detail(request, id):
    task = Ticket.objects.get(task_id=str(id))
    if request.user.is_superuser or int(task.responsible) == request.user.b24_contact_id:
        if not request.user.is_superuser:
            Ticket.objects.filter(task_id=str(id)).update(is_opened=True)
            status_closed = Ticket.objects.filter(responsible=str(request.user.b24_contact_id),  status__name='Closed').count()
            status_overdue = Ticket.objects.filter(responsible=str(request.user.b24_contact_id),  status__name='Overdue').count()
            status_ongoin = Ticket.objects.filter(responsible=str(request.user.b24_contact_id),  status__name='Ongoing').count()

            get_comments = TicketComments.objects.filter(ticket=Ticket.objects.get(task_id=str(id)))
            for comment in get_comments:
                comment.is_opened = True
                comment.save()
        else:
            status_closed = 0
            status_overdue = 0
            status_ongoin = 0

        # get comment from bitrix
        # url = set_webhook()
        # bx24 = Bitrix24(url)
        # section_list = bx24.callMethod('task.commentitem.getlist', taskId=int(id))
        all_created_comments = TicketComments.objects.filter(ticket=Ticket.objects.get(task_id=str(id))).order_by('created_date')
        comments_array = []
        for created_comment in all_created_comments:
            print('created_comment', created_comment)
            # test = datetime.strptime(created_comment.created_date, '%B.%d.%YT%H:%M:%S')

            # unset comment if message have "Author assigned:" text
            if "Author assigned:" in created_comment.text:
                continue
            if "Responsible person assigned:" in created_comment.text:
                continue    

            comment_time = created_comment.created_date
            formatted_date = comment_time.strftime("%B %d, %Y, %I:%M %p")
            if created_comment.added_documents_url != None:
                # file_name = os.path.basename(created_comment.added_documents_url.name)
                file_url = created_comment.added_documents_url
                # file_name = file_url.split("/")[-1]
                file_name = created_comment.added_document_name
                file_type = created_comment.added_document_type
            else:
                file_name = ""    
                file_url = "" 
                file_type = "" 
            
            comments_array.append({
                'bitrix_id': created_comment.comment_id,
                'message': created_comment.text,
                'sender': created_comment.manager_name,
                'data': formatted_date,
                # 'file': f'/media/{created_comment.added_documents}',
                'file': file_url,
                'file_name': file_name,
                'file_type': file_type,
            })

        res = {
            'task': task,
            'status_closed': status_closed,
            'status_overdue': status_overdue,
            'status_ongoin': status_ongoin,
            'comments': comments_array,
        }
        return render(request, "tickets/detail.html", res)
    else:
        return redirect('/tickets/')


def create_bitrix_task(request):
    if request.method == 'POST':
        responsible = str(request.user.b24_contact_id)
        task_name = request.POST.get('task_name')
        task_description = request.POST.get('task_description')
        # task_deadline = request.POST.get('task_deadline') if not 'NoneType' else datetime.today().strftime("%b.%d.%Y")
        request_deadline = request.POST.get('task_deadline')

        if not request_deadline == '':
            task_deadline = datetime.strptime(request_deadline, "%B.%d.%Y").strftime("%Y-%m-%d")
        else:
            task_deadline = datetime.today().strftime("%Y-%m-%d")

        # if file is added in task
        if request.FILES.getlist('userfile[]'):
            files = request.FILES.getlist('userfile[]')
            for file in files:
                file_name = file.name.replace(" ", "_")
                file_content_type = file.content_type
                file_path = os.path.join(settings.MEDIA_ROOT, 'comment_files', file_name)
                with open(file_path, 'wb') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
                domain = request.POST.get('domain')
                file_url = f'{domain}/media/comment_files/{file_name}'
                post_message = f'{task_description}\n' \
                               f'nexxess_file:{file_url}'
        else:
            post_message = task_description


        try:
            method = "tasks.task.add"
            url = set_webhook(method)
            payload = {
                'fields': {
                    'TITLE': task_name,
                    'DESCRIPTION': post_message,
                    'DEADLINE': task_deadline,
                    'CREATED_BY': 393, # 393
                    'RESPONSIBLE_ID': 312, # 312
                    'PRIORITY': 0,
                    'ALLOW_CHANGE_DEADLINE': 1,
                    'UF_CRM_TASK': {
                        "0": 'C_' + responsible,  # bitrix24_id
                        }
                    }
                }

            response = requests.post(url, json=payload)
            response_data = json.loads(response.content)
            task_id = response_data['result']['task']['id']

            if response.status_code == 200:
                time.sleep(3)
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

    # script for tags in b24 task
    # url = set_webhook()
    # bx24 = Bitrix24(url)
    # ticket = bx24.callMethod('tasks.task.list', order={'ID': "ASC"},
    #                           filter={"ID": 550, "LOAD_TAGS": "Y"},
    #                           select=["ID", "LOAD_TAGS"])

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


@csrf_exempt
def send_user_message(request):
    if request.method == "POST":
        user_message = request.POST.get('user_message')
        ticked_id = request.POST.get('ticked_id')

        url = set_webhook()
        bx24 = Bitrix24(url)

        # if added file in comments
        if request.FILES.get('file'):
            file = request.FILES.get('file')
            file_name = file.name
            file_content_type = file.content_type
            if file_content_type.startswith('image/'):
                file_type = "image"
            else:    
                file_type = "document"
            
            # save file localy in media folder
            file_path = os.path.join(settings.MEDIA_ROOT, 'comment_files', file_name)
            with open(file_path, 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            # comment with file
            domain = request.POST.get('site_domain')
            file_url = f'{domain}/media/comment_files/{file_name}'
            post_message = f'{user_message}\n' \
                           f'nexxess_file:{file_url}'
            added_file = True

            # url = set_webhook()
            # bx24 = Bitrix24(url)
            # image_name = "image.jpeg"
            # folder_id = 5951    # folder file "Files from tickets"
            # get_file = bx24.callMethod('disk.folder.getchildren', id=folder_id, filter={"NAME": image_name, "TYPE": "file"})
            # if get_file:
            #     print('get_file', get_file[0]["ID"])
            # else:
            #     file_path = "/home/nexxessdev/nexxess_main/nexxess-back-end/media/comment_files/image.jpeg"
            #     with open(file_path, 'rb') as f:
            #         content = f.read()
            #         f.close()
            #     added_file = bx24.callMethod('disk.folder.uploadfile', id=folder_id, data={"NAME": image_name}, fileContent=[image_name, content])
            
            # add comment in task in bitrix
            new_comment = bx24.callMethod('task.commentitem.add', taskId=ticked_id,
                                          fields={"AUTHOR_ID": 393, "POST_MESSAGE": post_message}) # AUTHOR_ID  393

            TicketComments.objects.create(
                ticket=Ticket.objects.get(task_id=ticked_id),
                comment_id=new_comment,
                text=user_message,
                manager_name="client",
                is_opened=True,
                added_documents_url=file_url,
                added_document_type=file_type,
                added_document_name=file_name,
                is_active=True,
                created_date=datetime.now(),
            )
        else:
            # comment without file
            post_message = user_message
            added_file = False
            file_name = None
            file_url = None
            file_type = None

            # add comment in task in bitrix
            new_comment = bx24.callMethod('task.commentitem.add', taskId=ticked_id,
                                          fields={"AUTHOR_ID": 393, "POST_MESSAGE": user_message}) # AUTHOR_ID  393

        now = datetime.now()
        formatted_date = now.strftime("%B %d, %Y, %I:%M %p")
        res = {
            'user_message': user_message,
            'ticked_id': ticked_id,
            'comment_created_data': formatted_date,
            'added_file': added_file,
            'file_name': file_name,
            'file_url': file_url,
            'file_type': file_type,
        }
        return JsonResponse(res)
