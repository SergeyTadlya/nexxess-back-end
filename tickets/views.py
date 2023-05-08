from django.shortcuts import render, redirect
from .models import Ticket
from .urls import *

import requests

def tasks(request):
    # відфільтровуємо дані по пошті авторизованого користувачі (адміну будуть виводитись всі)
    tasks_list = Ticket.objects.all() if request.user.is_superuser else Ticket.objects.filter(responsible=request.user.email)

    tasks_array = []
    for task in tasks_list:
        tasks_array.append({
            'id': task.id,
            'responsible': task.responsible,
            'task_id': task.task_id,
            'is_opened': task.is_opened,
        })

    context = {
        "tasks": tasks_array,
        'tasks_number': len(tasks_array),
    }
    return render(request, "tickets/tickets.html", context)


def task_detail(request, id):
    task = Ticket.objects.get(id=id)
    if request.user.is_superuser or task.responsible == request.user.email:
        # апдейт задачі, коли менеджер відкрив її (це щоб на головній сторінці, вона зникла із списка нових задач)
        if not request.user.is_superuser:
            Ticket.objects.filter(id=id).update(is_opened=True)

        res = {
            'task': task,
        }
        return render(request, "tickets/detail.html", res)
    else:
        return redirect('/tickets/')


def task_data(request):
    return render(request, 'tickets/list.html')
