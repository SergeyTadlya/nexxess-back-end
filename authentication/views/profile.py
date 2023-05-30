from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import JsonResponse

from telegram_bot.models import User
from tickets.models import Ticket, TicketStatus
from invoices.models import *


@login_required(login_url='/accounts/login/')
def profile_view(request):
    user = User.objects.filter(id=request.user.id)
    if user.exists():
        user = user.first()

    if request.method == 'POST':

        if request.FILES:
            if request.FILES['profile_image'].size < (2 * 1024 * 1024):
                file = request.FILES['profile_image']
                default_storage.save(file.name, file)  # Save image to /media/
                user.photo = file.name

        username = request.POST.get('username', '')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')

        check_list = [username, first_name, last_name, old_password]

        if new_password == '':
            user.username = username if username is not None else request.user.username
            user.first_name = first_name if first_name is not None else request.user.first_name
            user.last_name = last_name if last_name is not None else request.user.last_name
            user.save()
            return redirect('/profile/')

        elif '' not in check_list and len(new_password) > 7 and any([
            authenticate(request, username=request.user.email, password=old_password),
            all([old_password == user.password, len(old_password) == 41])],):
            user.username = username if username is not None else request.user.username
            user.first_name = first_name if first_name is not None else request.user.first_name
            user.last_name = last_name if last_name is not None else request.user.last_name
            user.set_password(new_password)
            user.google_auth = False
            user.save()

        else:
            return redirect('/profile/')

        return redirect('/accounts/login/')

    elif request.method == 'GET':
        user.first_name = 'First name' if user.first_name is None else user.first_name
        user.last_name = 'Last name' if user.last_name is None else user.last_name
        user.username = 'Username' if user.username is None else user.username
        user.save()

    all_user_tickets = Ticket.objects.all().order_by('-created_at') if request.user.is_superuser \
        else Ticket.objects.filter(responsible=request.user.b24_contact_id).order_by('-created_at')

    bought_services = Invoice.objects.filter(responsible=str(request.user.b24_contact_id), status__value='Paid')

    all_tickets_statuses = TicketStatus.objects.all()
    tickets_statuses = list()
    status_check = list()

    for ticket in all_user_tickets:
        for ticket_status in all_tickets_statuses:

            if ticket_status.name == ticket.status.name:
                ticket_status_quantity = all_user_tickets.filter(status__name=ticket_status.name).count()

                if ticket.status.name not in status_check:
                    status_check.append(ticket.status.name)
                    tickets_statuses.append({
                                    'name': ticket.status.name,
                                    'color': ticket.status.color,
                                    'number': ticket_status_quantity
                                    })

    context = {
        'user': user,
        'statuses': tickets_statuses,
        'bought_services': bought_services,
    }

    return render(request, 'profile.html', context)


def ajax_errors(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        if request.method == 'POST':

            username = request.user.username if request.user.username else 'Username'
            first_name = request.user.first_name if request.user.first_name else 'First name'
            last_name = request.user.last_name if request.user.last_name else 'Last name'

            response = {
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
            }

            return JsonResponse(response)
