from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.http import JsonResponse

from authentication.helpers.B24Webhook import set_webhook
from telegram_bot.models import User
from tickets.models import Ticket, TicketStatus
from invoices.models import Invoice

from bitrix24 import Bitrix24


@login_required(login_url='/accounts/login/')
def profile_view(request):
    user = User.objects.filter(id=request.user.id)
    if user.exists():
        user = user.first()

    if user.is_superuser:
        user_tickets = Ticket.objects.all().order_by('-created_at')
    else:
        user_tickets = Ticket.objects.filter(responsible=user.b24_contact_id).order_by('-created_at')

    paid_services = Invoice.objects.filter(responsible=str(user.b24_contact_id), status__value='Paid')

    tickets_statuses = TicketStatus.objects.all()
    statuses_list = list()
    status_check = list()

    for ticket in user_tickets:
        for ticket_status in tickets_statuses:

            if ticket_status.name == ticket.status.name:
                ticket_status_quantity = user_tickets.filter(status__name=ticket_status.name).count()

                if ticket.status.name not in status_check:
                    status_check.append(ticket.status.name)
                    statuses_list.append({
                        'name': ticket.status.name,
                        'color': ticket.status.color,
                        'number': ticket_status_quantity
                    })

    if request.method == 'POST':

        url = set_webhook()
        bx24 = Bitrix24(url)

        if request.FILES:
            if request.FILES['profile_image'].size < (2 * 1024 * 1024):
                file = request.FILES['profile_image']
                default_storage.save(file.name, file)  # Save image to /media/
                user.photo = file.name

        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone = request.POST.get('phone', '')
        bio = request.POST.get('bio', '')

        country = request.POST.get('country', '')
        city = request.POST.get('city', '')
        street = request.POST.get('street', '')
        tax_id = request.POST.get('tax_id', '')

        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')

        check_list = [first_name, last_name, phone, bio, country, city, street, tax_id, old_password]

        if new_password == '':

            user.first_name = first_name if first_name else user.first_name
            user.last_name = last_name if last_name else user.last_name
            user.phone = phone if phone else user.phone
            user.bio = bio if bio else user.bio

            user.country = country if country else user.country
            user.city = city if city else user.city
            user.street = street if street else user.street
            user.tax_id = tax_id if tax_id else user.tax_id

            data = bx24.callMethod('user.get', {"ID": 312})
            print(f'  >>>>>>>>>>>>>>  {data}')

            user.save()

            return redirect('/profile/')

        elif '' not in check_list and len(new_password) > 7 and any([authenticate(request, username=user.email, password=old_password), all([old_password == user.password, len(old_password) == 41])], ):

            user.first_name = first_name if first_name else user.first_name
            user.last_name = last_name if last_name else user.last_name
            user.phone = phone if phone else user.phone
            user.bio = bio if bio else user.bio

            user.country = country if country else user.country
            user.city = city if city else user.city
            user.street = street if street else user.street
            user.tax_id = tax_id if tax_id else user.tax_id

            user.set_password(new_password)
            user.google_auth = False

            user.save()

        else:
            return redirect('/profile/')

        return redirect('/accounts/login/')

    user.first_name = user.first_name if user.first_name else 'Empty'
    user.last_name = user.last_name if user.last_name else 'Empty'
    user.phone = user.phone if user.phone else 'Empty'
    user.bio = user.bio if user.bio else 'Empty'

    user.country = user.country if user.country else 'Empty'
    user.city = user.city if user.city else 'Empty'
    user.street = user.street if user.street else 'Empty'
    user.tax_id = user.tax_id if user.tax_id else 'Empty'

    context = {
        'user': user,
        'statuses': statuses_list,
        'paid_services': paid_services,
    }

    return render(request, 'profile.html', context)


def ajax_errors(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':

        if request.method == 'POST':

            response = {
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'phone': request.user.phone,
                'bio': request.user.bio,
                'country': request.user.country,
                'city': request.user.city,
                'street': request.user.street,
                'tax_id': request.user.tax_id,
            }

            return JsonResponse(response)
