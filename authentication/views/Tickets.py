from django.shortcuts import render, redirect
from authentication.models import Ticket


def tasks(request):
    # відфільтровуємо дані по пошті авторизованого користувачі (адміну будуть виводитись всі)
    if request.user.is_superuser:
        tasks_list = Ticket.objects.all()
    else:
        tasks_list = Ticket.objects.filter(responsible=request.user.email)

    arTask = []
    for task in tasks_list:
        arTask.append({
            'id': task.id,
            'responsible': task.responsible,
            'task_id': task.task_id,
            'is_opened': task.is_opened,
        })
    res = {
        "tasks": arTask
    }
    return render(request, "tickets/list.html", res)


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